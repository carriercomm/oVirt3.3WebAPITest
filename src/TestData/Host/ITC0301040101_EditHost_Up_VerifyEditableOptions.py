#encoding:utf-8


from Configs import GlobalConfig
import ITC03_SetUp as DM

'''
@note: Pre-TestData
'''
init_name = 'node-ITC0301040101'
xml_host_info = '''
<host>
    <name>%s</name>
    <address>%s</address>
    <root_password>%s</root_password>
    <cluster>
        <name>%s</name>
    </cluster>
</host>
''' % (init_name, GlobalConfig.Hosts['node4']['ip'], GlobalConfig.Hosts['node4']['password'], DM.cluster_name)

'''
@note: Test-Data
'''
new_name = 'node-ITC03010401-new'
new_desc = 'new description'
xml_update_info = '''
<host>
    <name>%s</name>
    <comment>%s</comment>
</host>
''' % (new_name, new_desc)

'''
@note: Post-TestData
'''
xml_host_del_option = '''
<action>
    <force>true</force>
    <async>false</async>
</action>
'''

'''
@note: ExpectedResult
'''
expected_status_code_create_host = 201          # 创建主机操作的期望状态码
expected_status_code_edit_host = 200            # 编辑主机操作的期望状态码
expected_status_code_deactive_host = 200        # 维护主机操作的期望状态码
expected_status_code_del_host = 200             # 删除主机操作的期望状态码
