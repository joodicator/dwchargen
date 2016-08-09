from __future__ import print_function

import threading
import traceback
import httplib
import weakref
import atexit
import random
import string
import time
import sys
import re

import selenium.common.exceptions
import selenium.webdriver

class Driver(selenium.webdriver.PhantomJS):
    __slots__ = 'pool'
    def __init__(self, pool, *args, **kwds):
        super(Driver, self).__init__(*args, **kwds)
        self.set_window_size(1360, 768)
        self.pool = pool
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.pool.release_driver(self)
    def log(self, action):
        print('*** Driver %x in pool %x %s.' % (
            id(self), id(self.pool), action))

class DriverPool(object):
    __slots__ = ('drivers', 'rlock', 'remove_driver_cond', 'destroyed',
                 'driver_cache_s', 'debug', '__weakref__')

    def __init__(self, driver_cache_s=60, debug=False):
        self.drivers = []
        self.rlock = threading.RLock()
        self.remove_driver_cond = threading.Condition(self.rlock)
        self.destroyed = False
        self.driver_cache_s = driver_cache_s
        self.debug = debug

        threading.Thread(
            name='DriverPool.run_pool(%r)' % self,
            target=self.run_pool,
            args=(threading.current_thread(),)
        ).start()

    def get_driver(self):
        driver = None
        with self.rlock:
            if self.destroyed: raise Exception(
                'This driver pool has been destroyed and is unusable.')
            if len(self.drivers):
                driver = self.drivers.pop(0)
                self.remove_driver_cond.notify_all()
                if self.debug: driver.log('removed')
            else:
                driver = Driver(self)
                if self.debug: driver.log('created and removed')
        return driver

    def release_driver(self, driver):
        with self.rlock:
            if self.destroyed: return
            if self.debug: driver.log('returned')
            self.drivers.append(driver)
            threading.Thread(
                name='DriverPool.destroy_driver(%r)' % driver,
                target=self.destroy_driver,
                args=(driver,)
            ).start()

    def destroy_driver(self, driver):
        start = time.time()
        remain = self.driver_cache_s
        with self.rlock:
            remove_driver_cond = self.remove_driver_cond
            while remain > 0:
                if driver not in self.drivers: return
                if self.destroyed: break
                remain = self.driver_cache_s - (time.time() - start)
                self, driver = weakref.ref(self), weakref.ref(driver)
                remove_driver_cond.wait(remain)
                self, driver = self(), driver()
                if self is None or driver is None: break
            if self is not None and driver is not None:
                self.drivers.remove(driver)
        if driver is not None:
            if self.debug: driver.log('destroyed')
            driver.quit()

    def run_pool(self, parent_thread):
        self = weakref.ref(self)
        parent_thread.join()
        self = self()
        if self is None: return
        with self.rlock:
            if self.debug: print(
                '*** Driver pool %x destroyed.' % id(self),
                file=sys.stderr)
            self.destroyed = True
            self.remove_driver_cond.notify_all()

pool = DriverPool(debug='--debug' in sys.argv[1:])

class NameGenerationException(Exception):
    def __init__(self, main_type, url, debug_file, driver, inner_exception):
        super(NameGenerationException, self).__init__(
        'Error retrieving names of type "%s" from <%s>.%s '
        'Original exception: %r' % (
            main_type, url,
            ' Response saved to %s.' % debug_file
            if debug_file is not None else '',
            inner_exception))

def random_name(*types):
    name, subtype = random_name_subtype(*types)
    return name

def random_name_gender(*types):
    (name, subtype) = random_name_subtype(*types)
    if subtype == 'amazon':
        subtype = 'female'
    if subtype not in ('male', 'female'):
        subtype = None
    return (name, subtype)

def random_name_subtype(*types):
    main_type = random.choice(types)
    exceptions = []
    for separator in '-', '_':
        try:
            return _random_name_subtype(
                'http://fantasynamegenerators.com/%s%snames.php'
                % (re.sub(r' ', separator, main_type.lower()), separator), main_type)
        except NameGenerationException as e:
            e.traceback = sys.exc_info()[2]
            exceptions.append(e)
    for exception in exceptions[:-1]:
        traceback.print_exception(exception, None, exception.traceback)
    raise exceptions[-1], None, exceptions[-1].traceback

def _random_name_subtype(url, main_type):
    with pool.get_driver() as phantomJS:
        try:
            phantomJS.implicitly_wait(0.5)
            phantomJS.get(url)
    
            nameGen = phantomJS.find_element_by_id('nameGen')
            buttons = nameGen.find_elements_by_tag_name('input')
            button = random.choice(buttons)
            subtype = button.get_attribute('value').lower()
            subtype = re.sub(r'(^get )(.*)( names$)', r'\2', subtype)
            button.click()

            names = phantomJS.find_element_by_id('result').text
            names = [name.strip() for name in re.split(r'[\r\n]+', names)]
            names = [string.capwords(name) for name in names if name]
            
            return (random.choice(names), subtype)
        except (
            selenium.common.exceptions.WebDriverException,
            httplib.HTTPException,
            IOError,
        ) as exc:
            exc_traceback = sys.exc_info()[2]
            try:
                debug_file = 'fantasynamegenerators.error.htm'
                with open(debug_file, 'w') as file:
                    file.write(phantomJS.page_source.encode('utf8'))
            except IOError:
                debug_file = None
            new_exc = NameGenerationException(main_type, url, debug_file, phantomJS, exc)
            raise new_exc, None, exc_traceback
