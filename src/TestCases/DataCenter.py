#encoding:utf-8
import xmltodict

__authors__ = ['"Liu Fei" <fei.liu@cs2c.com.cn>']
__version__ = "V0.1"

'''
# ChangeLog:
#---------------------------------------------------------------------------------
# Version        Date                Desc                            Author
#---------------------------------------------------------------------------------
# V0.1           2014/09/23          初始版本                                                            Liu Fei 
#---------------------------------------------------------------------------------
'''

import unittest

from BaseTestCase import BaseTestCase
from TestAPIs.DataCenterAPIs import DataCenterAPIs
from Utils.PrintLog import LogPrint

class ITC0101_GetDataCentersList(BaseTestCase):
    '''
    Summary:
    '''
    def test_GetDataCentersList(self):
        dcapi = DataCenterAPIs()
        r = dcapi.getDataCentersList()
        if r['status_code']==200:
            LogPrint().info('Get DataCenters list SUCCESS.')
            self.flag = True
        else:
            LogPrint().error('Get DataCenters list FAIL.')
            self.flag = False
        self.assertTrue(self.flag)
        
class ITC010201_GetDataCenterInfo(BaseTestCase):
    '''
    '''
    def setUp(self):
        # 调用父类方法，获取该用例所对应的测试数据模块
        self.dm = super(self.__class__, self).setUp()
        
        # 准备1：创建一个数据中心
        self.dcapi = DataCenterAPIs()
        self.dcapi.createDataCenter(self.dm.dc_info)
        
    def test_GetDataCenterInfo(self):
        # 测试1：获取数据中心的信息，并与期望结果进行对比
        r = self.dcapi.getDataCenterInfo(self.dm.dc_name)
        if r['status_code']==200:
            dict_actual = r['result']
            print dict_actual
            dict_expected = xmltodict.parse(self.dm.dc_info)
            print dict_expected
            self.assertDictContainsSubset(dict_expected, dict_actual)
        else:
            LogPrint().error("Create DataCenter '%s' FAILED. " % self.dm.dc_name)
    
    def tearDown(self):
        # 资源回收：删除所创建的数据中心
        if self.dcapi.searchDataCenterByName(self.dm.dc_name):
            self.dcapi.delDataCenter(self.dm.dc_name)

    
            


if __name__ == "__main__":
    # 建立测试套件 testSuite，并添加多个测试用例
    test_cases = ["DataCenter.ITC010201_GetDataCenterInfo"]
  
    testSuite = unittest.TestSuite()
    loader = unittest.TestLoader()
    tests = loader.loadTestsFromNames(test_cases)
    testSuite.addTests(tests)
 
    unittest.TextTestRunner(verbosity=2).run(testSuite)