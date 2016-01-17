from __future__ import print_function

import threading
import traceback
import weakref
import random
import string
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
    __slots__ = 'drivers', 'rlock', 'remove_driver_cond', 'driver_cache_s', 'debug'
    def __init__(self, driver_cache_s=300, debug=False):
        self.drivers = []
        self.rlock = threading.RLock()
        self.remove_driver_cond = threading.Condition(self.rlock)
        self.driver_cache_s = driver_cache_s
        self.debug = debug
    def get_driver(self):
        driver = None
        with self.rlock:
            if len(self.drivers):
                driver = self.drivers.pop(0)
                self.remove_driver_cond.notify_all()
                if self.debug: driver.log('removed')
            else:
                driver = Driver(self)
                if self.debug: driver.log('created')
        return driver
    def release_driver(self, driver):
        with self.rlock:
            if self.debug: driver.log('released')
            self.drivers.append(driver)
            thread = threading.Thread(target=self.destroy_driver, args=(driver,))
            thread.daemon = True
            thread.start()
    def destroy_driver(self, driver):
        with self.rlock:
            self.remove_driver_cond.wait(self.driver_cache_s)
            if driver not in self.drivers: return
            self.drivers.remove(driver)
            if self.debug: driver.log('destroyed')
        driver.quit()

pool = DriverPool()

class NameGenerationException(Exception):
    def __init__(self, type, url, debug_file, driver, inner_exception):
        super(NameGenerationException, self).__init__(
        'Error retrieving names of type "%s" from <%s>.%s '
        'Original exception: %s' % (
            type, url,
            ' Response saved to %s.' % debug_file
            if debug_file is not None else '',
            inner_exception))

def random_name(type):
    name, subtype = random_name_subtype(type)
    return name

def random_name_subtype(type):
    exceptions = []
    for separator in '-', '_':
        try:
            return _random_name_subtype(
                'http://fantasynamegenerators.com/%s%snames.php'
                % (re.sub(r' ', separator, type.lower()), separator), type)
        except NameGenerationException as e:
            exceptions.append(e)
    for exception in exceptions[:-1]:
        print(exception, file=sys.stderr)
    raise exceptions[-1]

def _random_name_subtype(url, type):
    with pool.get_driver() as phantomJS:
        phantomJS.implicitly_wait(0.5)
        try:
            if re.sub(r'#.*$', '', phantomJS.current_url) != url:
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
        except selenium.common.exceptions.WebDriverException as e:
            try:
                debug_file = 'fantasynamegenerators.error.htm'
                with open(debug_file, 'w') as file:
                    file.write(phantomJS.page_source.encode('utf8'))
            except IOError:
                traceback.print_exc()
                debug_file = None
            raise NameGenerationException(type, url, debug_file, phantomJS, e)
