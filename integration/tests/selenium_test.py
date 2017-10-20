from selenium import webdriver
import unittest

HOST = "127.0.0.1"
PORT = 5000

def startServer():
  hello.app.run()

class FlaskrTestCase(unittest.TestCase):

  def setUp(self):
    self.browser = webdriver.Firefox()
    self.browser.implicitly_wait(20)
#
#    from multiprocessing import Process
#    self.process = Process(target=startServer)
#    print(self.process)
#    import time
#    time.sleep(3)


  def tearDown(self):
    self.browser.quit()
    # shutdown the flask server
#    self.process.terminate()
    #self.process.kill()

  def test_hello(self):
    print('http://%s:%s' % (HOST,  PORT))
    self.browser.get('http://%s:%s' % (HOST,  PORT))
    print("Full Source")
    print (self.browser.page_source)
    
    assert 1 == 1
         



if __name__ == '__main__':
    unittest.main()



#browser = webdriver.Firefox()
#browser.implicitly_wait(20)
#
#HOST = "127.0.0.1"
#PORT = 5000
#
#try:
#  print('http://%s:%s' % (HOST,  PORT))
#  browser.get('http://%s:%s' % (HOST,  PORT))
#  print("Full Source")
#  print (browser.page_source)
#
#  #print('Just Body')
#  #print(browser.find_element_by_name('body').text)
#except:
#  print('Errors in the get')
#  import traceback
#  print(traceback.print_exc())
#
#browser.quit()
