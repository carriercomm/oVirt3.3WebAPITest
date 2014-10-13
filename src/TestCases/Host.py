#encoding:utf-8

__authors__ = ['"Liu Fei" <fei.liu@cs2c.com.cn>']
__version__ = "V0.1"

'''
# ChangeLog:
#---------------------------------------------------------------------------------
# Version        Date                Desc                            Author
#---------------------------------------------------------------------------------
# V0.1           2014/10/09          初始版本                                                            Liu Fei 
#---------------------------------------------------------------------------------
'''

import unittest

import xmltodict

from BaseTestCase import BaseTestCase
from TestAPIs.DataCenterAPIs import DataCenterAPIs
from TestAPIs.HostAPIs import HostAPIs
from TestAPIs.ClusterAPIs import ClusterAPIs
from Utils.PrintLog import LogPrint
from Utils.Util import DictCompare
from Utils.Util import wait_until
from TestData.Host import ITC03_SetUp as ModuleData


class ITC03_SetUp(BaseTestCase):
    '''
    @summary: “主机管理”模块测试环境初始化（执行该模块测试用例时，都需要执行该用例搭建初始化环境）
    @note: （1）创建一个数据中心（NFS）；
    @note: （2）创建一个集群；
    '''
    def setUp(self):
        '''
        @summary: 模块测试环境初始化（获取测试数据
        '''
        # 调用父类方法，获取该用例所对应的测试数据模块
        self.dm = super(self.__class__, self).setUp()

    def test_Create_DC_Cluster(self):
        '''
        @summary: 创建一个数据中心和一个集群
        '''
        dcapi = DataCenterAPIs()
        capi = ClusterAPIs()
        LogPrint().info("Pre-Module-Test: Create DataCenter '%s'." % self.dm.dc_name)
        dcapi.createDataCenter(self.dm.dc_info)
        LogPrint().info("Module Test Case: Create Cluster '%s' in DataCenter '%s'." % (self.dm.cluster_name, self.dm.dc_name))
        capi.createCluster(self.dm.cluster_info)
        
class ITC03_TearDown(BaseTestCase):
    '''
    @summary: “主机管理”模块测试环境清理（执行完该模块所有测试用例后，需要执行该用例清理环境）
    @note: （1）删除集群；
    @note: （2）删除数据中心；
    '''
    def test_TearDown(self):
        dcapi = DataCenterAPIs()
        capi = ClusterAPIs()
        if capi.searchClusterByName(ModuleData.cluster_name)['result']['clusters']:
            LogPrint().info("Post-Module-Test: Delete Cluster '%s'." % ModuleData.cluster_name)
            capi.delCluster(ModuleData.cluster_name)
        if dcapi.searchDataCenterByName(ModuleData.dc_name)['result']['data_centers']:
            LogPrint().info("Post-Module-Test: Delete DataCenter '%s'." % ModuleData.dc_name)
            dcapi.delDataCenter(ModuleData.dc_name)


class ITC030101_GetHostsList(BaseTestCase):
    '''
    @summary: ITC-03主机管理-01主机操作-01获取主机列表
    '''
    def test_GetDataCentersList(self):
        host_api = HostAPIs()
        r = host_api.getHostsList()
        if r['status_code']==200:
            LogPrint().info('PASS: Get Hosts list SUCCESS.')
        else:
            LogPrint().error('FAIL: Get Hosts list FAILED. Returned status code "%s" is incorrect.' % r['status_code'])
            self.flag = False
        self.assertTrue(self.flag)
        
class ITC030102_GetHostInfo(BaseTestCase):
    '''
    @summary: ITC-03主机管理-01主机操作-02查看主机信息
    '''
    def setUp(self):
        '''
        @summary: 测试环境准备－创建1个主机，并将其加入到模块级的数据中心和集群中。
        '''
        # 调用父类方法，获取该用例所对应的测试数据模块
        self.dm = super(self.__class__, self).setUp()
        self.host_api = HostAPIs()
        LogPrint().info('Pre-Test: Create Host "%s" in Cluster "%s".' % (self.dm.host_name, ModuleData.cluster_name))
        self.host_api.createHost(self.dm.xml_host_info)
        
    def test_GetHostInfo(self):
        '''
        @summary: 测试用例执行步骤
        @note: 查询指定主机信息
        @note: 验证接口返回状态验证码、结果是否正确
        '''
        self.flag = True
        def is_host_up():
            return self.host_api.getHostStatus(self.dm.host_name)=='up'
        if wait_until(is_host_up, 120, 5):
            r = self.host_api.getHostInfo(self.dm.host_name)
            if r['status_code']==self.dm.status_code:
                dictCompare = DictCompare()
                d1 = xmltodict.parse(self.dm.xml_host_info)
                del d1['host']['root_password']
                if dictCompare.isSubsetDict(d1, r['result']):
                    LogPrint().info("PASS: Get host '%s' info SUCCESS." % self.dm.host_name)
                else:
                    LogPrint().error("FAIL: Get host info incorrectly.")
                    self.flag = False
            else:
                LogPrint().error("FAIL: Returned status code '%s' is INCORRECT." % r['status_code'])
                self.flag = False
            self.assertTrue(self.flag)
        
    def tearDown(self):
        '''
        @summary: 资源回收（删除创建的主机）
        '''
        def is_host_maintenance():
            return self.host_api.getHostStatus(self.dm.host_name)=='maintenance'
        if self.host_api.searchHostByName(self.dm.host_name)['result']['hosts']:
            LogPrint().info("Post-Test: Deactive the host '%s' to maintenance state." % self.dm.host_name)
            self.host_api.deactiveHost(self.dm.host_name, self.dm.xml_del_option)
            if wait_until(is_host_maintenance, 120, 5):
                LogPrint().info("Post-Test: Delete the host '%s' from cluster." % self.dm.host_name)
                self.host_api.delHost(self.dm.host_name, self.dm.xml_del_option)

class ITC03010301_CreateHost_Normal(BaseTestCase):
    '''
    @summary: ITC-03主机管理-01主机操作-03创建-01常规创建
    '''
    def setUp(self):
        '''
        @summary: 测试环境准备－创建1个主机，并将其加入到模块级的数据中心和集群中。
        '''
        # 调用父类方法，获取该用例所对应的测试数据模块
        self.dm = super(self.__class__, self).setUp()
        self.host_api = HostAPIs()
        
    def test_GetHostInfo(self):
        '''
        @summary: 测试用例执行步骤
        @note: 查询指定主机信息
        @note: 验证接口返回状态验证码、结果是否正确
        '''
        self.flag = True
        LogPrint().info('Pre-Test: Create Host "%s" in Cluster "%s".' % (self.dm.host_name, ModuleData.cluster_name))
        r = self.host_api.createHost(self.dm.xml_host_info)
        def is_host_up():
            return self.host_api.getHostStatus(self.dm.host_name)=='up'
        if wait_until(is_host_up, 200, 5):
            if r['status_code']==self.dm.status_code:
                dictCompare = DictCompare()
                d1 = xmltodict.parse(self.dm.xml_host_info)
                del d1['host']['root_password']
                if dictCompare.isSubsetDict(d1, r['result']):
                    LogPrint().info("PASS: Create host '%s' SUCCESS." % self.dm.host_name)
                else:
                    LogPrint().error("FAIL: Returned info of created host are incorrectly.")
                    self.flag = False
            else:
                LogPrint().error("FAIL: Returned status code '%s' is INCORRECT." % r['status_code'])
                self.flag = False
        else:
            self.flag = False
            LogPrint().error("FAIL: Create host '%s' FAILED. The state of host is '%s'." % (self.dm.host_name, self.host_api.getHostStatus(self.dm.host_name)))

        
    def tearDown(self):
        '''
        @summary: 资源回收（删除创建的主机）
        '''
        def is_host_maintenance():
            return self.host_api.getHostStatus(self.dm.host_name)=='maintenance'
        if self.host_api.searchHostByName(self.dm.host_name)['result']['hosts']:
            LogPrint().info("Post-Test: Deactive the host '%s' to maintenance state." % self.dm.host_name)
            self.host_api.deactiveHost(self.dm.host_name)
            if wait_until(is_host_maintenance, 120, 5):
                LogPrint().info("Post-Test: Delete the host '%s' from cluster." % self.dm.host_name)
                self.host_api.delHost(self.dm.host_name, self.dm.xml_del_option)
        
class ITC03010303_CreateHost_DupName(BaseTestCase):
    '''
    @summary: ITC-03主机管理-01主机操作-03创建-03重名
    '''
    def setUp(self):
        '''
        @summary: 测试环境准备
        @note: 创建1个主机
        '''
        # 调用父类方法，获取该用例所对应的测试数据模块
        self.dm = super(self.__class__, self).setUp()
        self.host_api = HostAPIs()
        self.host_api.createHost(self.dm.xml_host_info)
    
    def test_CreateHost_DupName(self):
        '''
        @summary: 测试步骤
        @note: （1）创建一个重名数据中心
        @note: （2）操作失败，验证接口返回状态码、返回提示信息是否正确。
        '''
        r = self.host_api.createHost(self.dm.xml_host_info)
        if r['status_code']==self.dm.status_code:
            dictCompare = DictCompare()
            d1 = xmltodict.parse(self.dm.expect_result)
            if dictCompare.isSubsetDict(d1, r['result']):
                LogPrint().info("PASS: Returned status code and messages are CORRECT when create host with dup name.")
            else:
                LogPrint().error("FAIL: Returned messages are incorrectly.")
                self.flag = False
        else:
            LogPrint().error("FAIL: Returned status code '%s' is INCORRECT." % r['status_code'])
            self.flag = False
            
    def tearDown(self):
        '''
        @summary: 清理资源
        @note: 删除创建的主机
        '''
        def is_host_up():
            return self.host_api.getHostStatus(self.dm.host_name)=='up'
        def is_host_maintenance():
            return self.host_api.getHostStatus(self.dm.host_name)=='maintenance'
        
        if self.host_api.searchHostByName(self.dm.host_name)['result']['hosts']:
            if wait_until(is_host_up, 120, 5):
                LogPrint().info("Post-Test: Deactive the host '%s' to maintenance state." % self.dm.host_name)
                self.host_api.deactiveHost(self.dm.host_name, self.dm.xml_del_option)
                if wait_until(is_host_maintenance, 120, 5):
                    LogPrint().info("Post-Test: Delete the host '%s' from cluster." % self.dm.host_name)
                    self.host_api.delHost(self.dm.host_name, self.dm.xml_del_option)

class ITC03010304_CreateHost_NameVerify(BaseTestCase):
    '''
    @summary: ITC-03主机管理-01主机操作-03创建-04名称有效性验证
    '''
    def setUp(self):
        '''
        @summary: 初始化测试环境（获取相应的测试数据）
        '''
        # 调用父类方法，获取该用例所对应的测试数据模块
        self.dm = super(self.__class__, self).setUp()
        self.host_api = HostAPIs()
        
    def test_CreateHost_NameVerify(self):
        '''
        @summary: 测试步骤
        @note: （1）输入各种不合法的name，创建主机；
        @note: （2）操作失败，验证接口返回的状态码、提示信息是否正确。
        '''
        # 本用例有多种测试情况，所以期望结果也有多种，这个变量代表期望结果的索引值
        self.expected_result_index = 0
        
        # 使用数据驱动，根据测试数据文件循环创建多个名称非法的主机
        @BaseTestCase.drive_data(self, self.dm.xml_host_info)
        def do_test(xml_info):
            self.flag = True
            r = self.host_api.createHost(xml_info)
            # 比较接口返回状态码、提示信息是否正确
            if r['status_code']==self.dm.expected_status_code:
                dictCompare = DictCompare()
                if dictCompare.isSubsetDict(xmltodict.parse(self.dm.expected_info_list[self.expected_result_index]), r['result']):
                    LogPrint().info("PASS: The returned status code and messages are CORRECT.")
                else:
                    LogPrint().error("FAIL: The returned messages are INCORRECT.")
                    self.flag = False
            else:
                LogPrint().error("FAIL: The returned status code is '%s' while it should be '%s'." % (r['status_code'], self.dm.expected_status_code))
                self.flag = False
            self.assertTrue(self.flag)
            self.expected_result_index += 1
            
        do_test()
    
    def tearDown(self):
        '''
        @summary: 资源清理，若上述主机创建成功则需要将其删除。
        '''
        pass
    
class ITC03010305_CreateHost_IpVerify(BaseTestCase):
    '''
    @summary: ITC-03主机管理-01主机操作-03创建-05IP有效性验证
    '''
    def setUp(self):
        '''
        @summary: 初始化测试环境
        '''
        self.dm = super(self.__class__, self).setUp()
        self.host_api = HostAPIs()
        
    def test_CreateHost_IpVerify(self):
        '''
        @summary: 测试步骤
        @note: （1）输入各种不合法的IP，创建主机；
        @note: （2）操作失败，验证接口返回的状态码、提示信息是否正确。
        '''
        # 使用数据驱动，根据测试数据文件循环创建多个名称非法的主机
        @BaseTestCase.drive_data(self, self.dm.xml_host_info)
        def do_test(xml_info):
            self.flag = True
            host_ip = xmltodict.parse(xml_info)['host']['address']
            r = self.host_api.createHost(xml_info)
            # 验证接口返回状态码是否正确
            if r['status_code'] == self.dm.expected_status_code:
                # 验证接口返回提示信息是否正确
                dictCompare = DictCompare()
                if dictCompare.isSubsetDict(xmltodict.parse(self.dm.expected_info), r['result']):
                    LogPrint().info("PASS: The returned status code and messages are CORRECT when create host with invalid IP address '%s'." % host_ip)
                else:
                    LogPrint().error("FAIL: The returned messages are INCORRECT when create host with the invalid IP address '%s'." % host_ip)
                    self.flag = False
            else:
                LogPrint().error("FAIL: The returned status code is '%s' while it should be '%s'." % (r['status_code'], self.dm.expected_status_code))
                self.flag = False
            self.assertTrue(self.flag)
            
        do_test()
            
    def tearDown(self):
        '''
        @summary: 资源清理（主机创建失败，不需要进行资源清理。）
        '''
        pass

class ITC03010306_CreateHost_IncorrectPassword(BaseTestCase):
    '''
    @summary: ITC-03主机管理-01主机操作-03创建-06root密码错误
    '''
    def setUp(self):
        '''
        @summary: 初始化测试环境
        '''
        self.dm = super(self.__class__, self).setUp()
        self.host_api = HostAPIs()
        
    def test_CreateHost_IncorrectIp(self):
        '''
        @summary: 测试步骤
        @note: （1）输入不正确的IP，创建主机；
        @note: （2）操作失败，验证接口返回的状态码、提示信息是否正确。
        '''
        r = self.host_api.createHost(self.dm.xml_host_info)
        # 判断接口返回状态码是否正确
        if r['status_code'] == self.dm.expected_status_code:
            dictCompare = DictCompare()
            # 判断接口返回提示信息是否正确
            if dictCompare.isSubsetDict(r['result'], xmltodict.parse(self.dm.expected_info)):
                LogPrint().info("PASS: The returned status code and messages are CORRECT when create host with incorrect password.")
            else:
                LogPrint().error("FAIL: The returned messages are INCORRECT when create host with incorrect password.")
                self.flag = False
        else:
            LogPrint().error("FAIL: The returned status code is '%s' while it should be '%s'." % (r['status_code'], self.dm.expected_status_code))
            self.flag = False
        self.assertTrue(self.flag)
        
    def tearDown(self):
        '''
        @summary: 资源清理（本用例主机创建失败，不需要进行清理）
        '''
        pass
    
class ITC03010307_CreateHost_NoRequiredParams(BaseTestCase):
    '''
    @summary: ITC-03主机管理-01主机操作-03创建-07缺少必填参数
    '''
    def setUp(self):
        '''
        @summary: 初始化测试环境
        '''
        self.dm = super(self.__class__, self).setUp()
        self.host_api = HostAPIs()
        
    def test_CreateHost_NoRequiredParams(self):
        '''
        @summary: 测试步骤
        @note: （1）缺少主机名称
        @note: （2）缺少主机地址
        @note: （3）缺少root密码
        @note: （4）缺少Cluster的情况下，缺省加入到Default集群中（此项测试不进行）
        @note: （5）创建主机失败，验证接口返回的状态码、提示信息是否正确
        '''
        # 本用例有多种测试情况，所以期望结果也有多种，该变量代表期望结果的索引值
        self.expected_result_index = 0
        
        # 使用数据驱动，根据测试数据文件循环创建多个缺少必要参数的主机
        @BaseTestCase.drive_data(self, self.dm.xml_host_info)
        def do_test(xml_info):
            self.flag = True
            r = self.host_api.createHost(xml_info)
            if r['status_code']==self.dm.expected_status_code:
                dictCompare = DictCompare()
                if dictCompare.isSubsetDict(xmltodict.parse(self.dm.expected_info_list[self.expected_result_index]), r['result']):
                    LogPrint().info("PASS: The returned status code and messages are CORRECT when create host without required params.")
                else:
                    LogPrint().error("FAIL: The returned messages are INCORRECT when create host without required params.")
                    self.flag = False
            else:
                LogPrint().error("FAIL: The returned status code is '%s' while it should be '%s'." % (r['status_code'], self.dm.expected_status_code))
                self.flag = False
            self.assertTrue(self.flag)
            self.expected_result_index += 1
            
        do_test()
        
    def tearDown(self):
        pass
    
class ITC0301040101_EditHost_Up_VerifyEditableOptions(BaseTestCase):
    '''
    @summary: ITC-03主机管理-01主机操作-04编辑-01Active状态-01验证可编辑项
    '''
    def setUp(self):
        '''
        @summary: 准备测试环境
        @note: （1）创建一个主机，等待其变为Up状态
        '''
        # 获取测试数据
        self.dm = super(self.__class__, self).setUp()
        
        # 创建一个主机，并等待其状态为Up。
        self.host_api = HostAPIs()
        self.flag = True
        LogPrint().info('Pre-Test-Step1: Create Host "%s" in Cluster "%s".' % (self.dm.init_name, ModuleData.cluster_name))
        r = self.host_api.createHost(self.dm.xml_host_info)
        def is_host_up():
            return self.host_api.getHostStatus(self.dm.init_name)=='up'
        if wait_until(is_host_up, 200, 5):
            if r['status_code']==self.dm.expected_status_code_create_host:
                LogPrint().info("Pre-Test-PASS: Create host '%s' SUCCESS." % self.dm.init_name)
            else:
                LogPrint().error("Pre-Test-FAIL: Returned status code '%s' is INCORRECT when create host '%s'." % (r['status_code'], self.dm.init_name))
                self.flag = False
        else:
            self.flag = False
            LogPrint().error("Pre-Test-FAIL: Create host '%s' FAILED. The state of host is '%s'." % (self.dm.init_name, self.host_api.getHostStatus(self.dm.init_name)))
        self.assertTrue(self.flag)
        
    def test_EditHost_Up_VerifyEditableOptions(self):
        '''
        @summary: 测试步骤
        @note: （1）在UP状态下修改可编辑的项：主机名称、描述；
        @note: （2）验证接口返回状态码、编辑后的信息是否正确。
        '''
        self.flag = True
        r = self.host_api.updateHost(self.dm.init_name, self.dm.xml_update_info)
        # 判断接口返回状态码是否正确
        if r['status_code'] == self.dm.expected_status_code_edit_host:
            dictCompare = DictCompare()
            # 判断接口返回的编辑后主机信息与修改的信息是否一致
            if dictCompare.isSubsetDict(xmltodict.parse(self.dm.xml_update_info), r['result']):
                LogPrint().info("PASS: Edit host's name and desc SUCCESS in UP state.")
            else:
                LogPrint().info("FAIL: The updated host's name and desc are different to expected.")
                self.flag = False
        else:
            LogPrint().info("FAIL: The returned status code '%s' by update option is INCORRECT, it should be '%s'." % (r['status_code'], self.dm.expected_status_code_edit_host))
            self.flag = False
        self.assertTrue(self.flag)

    def tearDown(self):
        '''
        @summary: 资源清理
        @note: 删除创建的主机
        '''
        
        for host_name in [self.dm.new_name, self.dm.init_name]:
            def is_host_maintenance():
                return self.host_api.getHostStatus(host_name)=='maintenance'
            if self.host_api.searchHostByName(host_name)['result']['hosts']:
                LogPrint().info("Post-Test: Deactive host '%s' from up to maintenance state." % host_name)
                r = self.host_api.deactiveHost(host_name)
                self.assertTrue(r['status_code']==self.dm.expected_status_code_deactive_host)
                if wait_until(is_host_maintenance, 120, 5):
                    LogPrint().info("Post-Test: Delete host '%s' from cluster." % host_name)
                    r = self.host_api.delHost(host_name, self.dm.xml_host_del_option)
                    self.assertTrue(r['status_code']==self.dm.expected_status_code_del_host)
                    
class ITC0301040102_EditHost_Up_VerifyUneditableOptions(BaseTestCase):
    '''
    @summary: ITC-03主机管理-01主机操作-04编辑-01Up状态-02验证不可编辑项
    '''
    def setUp(self):
        '''
        @summary: 准备测试环境
        @note: （1）创建一个主机，等待其变为Up状态；
        '''
        # 获取测试数据
        self.dm = super(self.__class__, self).setUp()
        
        # 创建一个主机，并等待其状态为Up。
        self.host_api = HostAPIs()
        self.flag = True
        LogPrint().info('Pre-Test-Step1: Create Host "%s" in Cluster "%s".' % (self.dm.host_name, ModuleData.cluster_name))
        r = self.host_api.createHost(self.dm.xml_host_info)
        def is_host_up():
            return self.host_api.getHostStatus(self.dm.host_name)=='up'
        if wait_until(is_host_up, 200, 5):
            if r['status_code']==self.dm.expected_status_code_create_host:
                LogPrint().info("Pre-Test-PASS: Create host '%s' SUCCESS." % self.dm.host_name)
            else:
                LogPrint().error("Pre-Test-FAIL: Returned status code '%s' is INCORRECT when create host '%s'." % (r['status_code'], self.dm.host_name))
                self.flag = False
        else:
            self.flag = False
            LogPrint().error("Pre-Test-FAIL: Create host '%s' FAILED. The state of host is '%s'." % (self.dm.host_name, self.host_api.getHostStatus(self.dm.init_name)))
        self.assertTrue(self.flag)
        
    def test_EditHost_Up_VerifyUneditableOptions(self):
        '''
        @summary: 测试步骤
        @note: （1）在UP状态下修改不可编辑的项：IP、密码、Cluster等；
        @note: （2）验证操作失败后，接口返回状态码、编辑后的信息是否正确。
        '''
        self.flag = True
        r = self.host_api.updateHost(self.dm.host_name, self.dm.xml_host_update_info)
        # 判断接口返回状态码是否正确
        if r['status_code'] == self.dm.expected_status_code_edit_host:
            dictCompare = DictCompare()
            # 判断接口返回的编辑后主机信息与修改的信息是否一致
            if dictCompare.isSubsetDict(xmltodict.parse(self.dm.expected_info_edit_host), r['result']):
                LogPrint().info("PASS: Returned status code and messages are CORRECT when modified the uneditable option the host in UP state.")
            else:
                LogPrint().info("FAIL: Returned messages are INCORRECT when modify the host's parameters with UP state.")
                self.flag = False
        else:
            LogPrint().info("FAIL: Returned status code '%s' by update option is INCORRECT, it should be '%s'." % (r['status_code'], self.dm.expected_status_code_edit_host))
            self.flag = False
        self.assertTrue(self.flag)

    def tearDown(self):
        '''
        @summary: 资源清理
        @note: 删除创建的主机
        '''
        def is_host_maintenance():
            return self.host_api.getHostStatus(self.dm.host_name)=='maintenance'
        if self.host_api.searchHostByName(self.dm.host_name)['result']['hosts']:
            LogPrint().info("Post-Test: Deactive host '%s' from up to maintenance state." % self.dm.host_name)
            r = self.host_api.deactiveHost(self.dm.host_name)
            self.assertTrue(r['status_code']==self.dm.expected_status_code_deactive_host)
            if wait_until(is_host_maintenance, 120, 5):
                LogPrint().info("Post-Test: Delete host '%s' from cluster." % self.dm.host_name)
                r = self.host_api.delHost(self.dm.host_name, self.dm.xml_host_del_option)
                self.assertTrue(r['status_code']==self.dm.expected_status_code_del_host)
                

class ITC0301040201_EditHost_Maintenance_VerifyEditableOptions(BaseTestCase):
    '''
    @summary: ITC-03主机管理-01主机操作-04编辑-02Maintenance状态-01验证可编辑项
    '''
    def setUp(self):
        '''
        @summary: 准备测试环境
        @note: （1）创建一个主机，等待其变为Up状态；
        @note: （2）在同一数据中心里创建一个新的Cluster；
        '''
        # 获取测试数据
        self.dm = super(self.__class__, self).setUp()
        
        # 创建一个主机，将其加入指定集群（ITC03_SetUp.py中指定的集群），并等待其状态为Up。
        self.host_api = HostAPIs()
        self.flag = True
        LogPrint().info('Pre-Test-Step1: Create Host "%s" in Cluster "%s".' % (self.dm.init_host_name, ModuleData.cluster_name))
        r = self.host_api.createHost(self.dm.xml_host_info)
        def is_host_up():
            return self.host_api.getHostStatus(self.dm.init_host_name)=='up'
        if wait_until(is_host_up, 200, 5):
            if r['status_code']==self.dm.expected_status_code_create_host:
                LogPrint().info("Pre-Test1-PASS: Create host '%s' SUCCESS." % self.dm.init_host_name)
            else:
                LogPrint().error("Pre-Test1-FAIL: Returned status code '%s' is INCORRECT when create host '%s'." % (r['status_code'], self.dm.init_host_name))
                self.flag = False
        else:
            self.flag = False
            LogPrint().error("Pre-Test1-FAIL: Create host '%s' FAILED. The state of host is '%s'." % (self.dm.init_host_name, self.host_api.getHostStatus(self.dm.init_host_name)))
        self.assertTrue(self.flag)
        
        # 在同一数据中心里创建一个新的集群（用于修改Host的所属Cluster时使用）
        self.cluster_api = ClusterAPIs()
        self.flag = True
        LogPrint().info('Pre-Test-Step2: Create a new cluster "%s" in DataCenter "%s".' % (self.dm.cluster1_name, ModuleData.dc_name))
        r = self.cluster_api.createCluster(self.dm.xml_cluster1_info)
        if r['status_code'] == self.dm.expected_status_code_create_cluster:
            LogPrint().info("Pre-Test2-PASS: Create a new Cluster '%s' SUCCESS." % self.dm.cluster1_name)
        else:
            LogPrint().error("Pre-Test2-FAIL: Create new Cluster '%s' FAILED." %self.dm.cluster1_name)
            self.flag = False
        self.assertTrue(self.flag)
        
    def test_EditHost_Maintenance_VerifyEditableOptions(self):
        '''
        @summary: 测试步骤
        @note: （1）在Maintenance状态下修改可编辑的项：主机名称、注释、所属集群；
        @note: （2）验证接口返回状态码、编辑后的信息是否正确。
        '''
        self.flag = True
        print self.dm.xml_host_update_info
        r = self.host_api.updateHost(self.dm.init_host_name, self.dm.xml_host_update_info)
        print r['status_code']
        print r['result']
        # 判断接口返回状态码是否正确
        if r['status_code'] == self.dm.expected_status_code_edit_host:
            dictCompare = DictCompare()
            # 判断接口返回的编辑后主机信息与修改的信息是否一致
            if dictCompare.isSubsetDict(xmltodict.parse(self.dm.xml_host_update_info), r['result']):
                LogPrint().info("PASS: Edit host's name/comment/cluster SUCCESS in Maintenance state.")
            else:
                LogPrint().info("FAIL: The updated host's name/comment/cluster are different to expected.")
                self.flag = False
        else:
            LogPrint().info("FAIL: The returned status code '%s' by update operation is INCORRECT, it should be '%s'." % (r['status_code'], self.dm.expected_status_code_edit_host))
            self.flag = False
        self.assertTrue(self.flag)

    def tearDown(self):
        '''
        @summary: 资源清理
        @note: （1）删除创建的主机；
        @note: （2）删除创建的集群。 
        '''
        # 删除主机
        for host_name in [self.dm.new_name, self.dm.init_host_name]:
            def is_host_maintenance():
                return self.host_api.getHostStatus(host_name)=='maintenance'
            if self.host_api.searchHostByName(host_name)['result']['hosts']:
                LogPrint().info("Post-Test: Deactive host '%s' from up to maintenance state." % host_name)
                r = self.host_api.deactiveHost(host_name)
                self.assertTrue(r['status_code']==self.dm.expected_status_code_deactive_host)
                if wait_until(is_host_maintenance, 120, 5):
                    LogPrint().info("Post-Test: Delete host '%s' from cluster." % host_name)
                    r = self.host_api.delHost(host_name, self.dm.xml_host_del_option)
                    self.assertTrue(r['status_code']==self.dm.expected_status_code_del_host)
        # 删除本用例中新建的Cluster
        if self.cluster_api.searchClusterByName(self.dm.cluster1_name)['result']['clusters']:
            LogPrint().info("Post-Test: Delete the created Cluster '%s' in this TestCase." % self.dm.cluster1_name)
            r = self.cluster_api.delCluster(self.dm.cluster1_name, self.dm.xml_cluster_del_option)
            self.assertTrue(r['status_code']==self.dm.expected_status_code_del_cluster)
    

if __name__ == "__main__":
    # 建立测试套件 testSuite，并添加多个测试用例
    test_cases = ["Host.ITC0301040201_EditHost_Maintenance_VerifyEditableOptions"]
  
    testSuite = unittest.TestSuite()
    loader = unittest.TestLoader()
    tests = loader.loadTestsFromNames(test_cases)
    testSuite.addTests(tests)
 
    unittest.TextTestRunner(verbosity=2).run(testSuite)

#     fileName = r"d:\result.html"
#     fp = file(fileName, 'wb')
#     runner = HTMLTestRunner(stream=fp, title=u"测试结果", description=u"测试报告")
#     runner.run(testSuite)