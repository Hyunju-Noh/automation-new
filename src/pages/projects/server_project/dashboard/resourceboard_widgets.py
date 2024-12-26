all_widgets = [
    
    {
        "widget_name": "OS",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('OS'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "Server",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Server'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "Total Cores",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Total Cores'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "Avg CPU",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg CPU'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "Avg Memory",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg Memory'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "Avg Disk",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg Disk'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "메모리 - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('메모리')))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "디스크 I/O - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('디스크 I/O')))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    # 이상하게 이거 검증이 안되네... UI에는 잘 뜨는데...
    # {
    #     "widget_name": "Server Status Map",
    #     "locator": "div.PanelContents__Wrapper-dAMbXP.eMnZTY:has(span:text('Server Status Map'))",  # 위젯 자체 확인
    #     "element_name": None,  # 내부 요소 없음
    #     "element_locator": None,
    #     "button_name": None,
    #     "action": None
    # },
    
    {
        "widget_name": "프로세스 CPU TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 CPU TOP5'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "프로세스 메모리 TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 메모리 TOP5'))",  # 위젯 자체 확인
        "element_name": None,  # 내부 요소 없음
        "element_locator": None,
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "Server",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Server'))",  # 위젯 자체 확인
        "element_name": "[>] button",
        "element_locator": "{locator} button.Styles__Button-bDBZvm",
        "button_name": "[>] button",
        "action": lambda page, test_results: verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="서버 목록 화면",
            expected_url="/server/list"
        )
    },
    {
        "widget_name": "Server",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Server'))",  # 위젯 자체 확인
        "element_name": "Value Text",
        "element_locator": "{locator} span.ResourceCards__ValueText-jMQaIH.fZMedF",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Server",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Server'))",  # 위젯 자체 확인
        "element_name": "Progress Bar",
        "element_locator": "{locator} div.ant-progress.ant-progress-line.ant-progress-status-active.ant-progress-default",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Server",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Server'))",  # 위젯 자체 확인
        "element_name": "Progress Bar Text",
        "element_locator": "{locator} div.ResourceCards__ProgressLabels-jdjbop.bkmXSU",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "OS",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('OS'))",  # 위젯 자체 확인
        "element_name": "OS elements",
        "element_locator": "{locator} div.ResourceCards__FlexRemainder-hCQgll.gORGxv",
        "button_name": None,
        "action": None,
        "child_count": None  # 예상되는 하위 요소 개수
    },
    {
        "widget_name": "Total Cores",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Total Cores'))",  # 위젯 자체 확인
        "element_name": "Value Text",
        "element_locator": "{locator} span.ResourceCards__ValueText-jMQaIH.fZMedF",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Avg CPU",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg CPU'))",  # 위젯 자체 확인
        "element_name": "Value Text",
        "element_locator": "{locator} span.ResourceCards__ValueText-jMQaIH.fZMedF",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Avg CPU",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg CPU'))",  # 위젯 자체 확인
        "element_name": "PercentBar",
        "element_locator": "{locator} div.PercentBarstyle__PercentBarWrapper-fuDbrY",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Avg Memory",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg Memory'))",  # 위젯 자체 확인
        "element_name": "Value Text",
        "element_locator": "{locator} span.ResourceCards__ValueText-jMQaIH.fZMedF",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Avg Memory",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg Memory'))",  
        "element_name": "PercentBar",
        "element_locator": "{locator} div.PercentBarstyle__PercentBarWrapper-fuDbrY",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Avg Disk",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg Disk'))", 
        "element_name": "Value Text",
        "element_locator": "{locator} span.ResourceCards__ValueText-jMQaIH.fZMedF",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "Avg Disk",
        "locator": "div.ResourceCards__CardDom-dzFtxX:has(span:text('Avg Disk'))",  
        "element_name": "PercentBar",
        "element_locator": "{locator} div.PercentBarstyle__PercentBarWrapper-fuDbrY",
        "button_name": None,  # 버튼이 없는 경우 None
        "action": None  # 동작 수행 함수 없음
    },
    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",
        "element_name": "info button",  
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.LPWtZ",
        "button_name": "info button",
        "action": lambda page, test_results: info_button_action(
            page=page,
            popover_locator="div.ant-popover.ant-popover-placement-bottom",  # Popover 부모 요소를 나타내는 조건
            popover_text_locator="div.HelperButton__ContentContainer-dPhKeC.eokXGu",  # 팝오버 텍스트 클래스
            expected_text="CPU",
            test_results=test_results,
        )
    },

    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",
        "element_name": "[>] button",
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.lomqVM",
        "button_name": "[>] button",
        "action":  lambda page, test_results: verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="리소스 이퀄라이저",
            expected_url="/dashboard/multi_line?content=cpu"
        )
    },

    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",
        "element_name": "PanelContents button",
        "element_locator": "{locator} .Ants__Dropdown-cCtpgz.bRdCUm",
        "button_name": "PanelContents button",
        "action": lambda page, test_results: dropdown_button_action(
            page=page,
            dropdown_locator="div.ant-dropdown.ant-dropdown-placement-bottomLeft",
            expected_left_value=947,
            test_results=test_results
        )
        
    },

    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",
        "element_name": "PanelContents chart",
        "element_locator": "{locator} canvas.sc-dcJsrY.dvDjBb",
        "button_name": "PanelContents chart",
        "action": lambda page, test_results: (
            verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="서버 상세",
            expected_url="/server_detail"
        ),
            #verify_agent(page, expected_agent, test_results)
        ),
        "hover_positions": [  
        {"x":120,"y":40}
        ] # 툴팁 검증을 위한 좌표
    },

    {
        "widget_name": "CPU - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('CPU')))",
        "element_name": "PanelContents dropdown",
        "element_locator": "{locator} .Ants__Dropdown-cCtpgz.bRdCUm",
        "button_name": "PanelContents dropdown",
        "action": lambda page, test_results: dropdown_button_action(
            page=page,
            dropdown_locator="div.ant-dropdown.ant-dropdown-placement-bottomLeft",
            expected_left_value=947,
            dropdown_list_button_locator='li:has-text("Disk Inode")',
            element_locator="div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('expected_text'))) .Ants__Dropdown-cCtpgz.bRdCUm",
            expected_text="Disk Inode",
            test_results=test_results
        )
        
    },

    {
        "widget_name": "memory - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('메모리')))",
        "element_name": "info button",  
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.LPWtZ",
        "button_name": "info button",
        "action": lambda page, test_results: info_button_action(
            page=page,
            popover_locator="div.ant-popover.ant-popover-placement-top",  # Popover 부모 요소를 나타내는 조건
            popover_text_locator="div.HelperButton__ContentContainer-dPhKeC.eokXGu",  # 팝오버 텍스트 클래스
            expected_text="메모리",
            test_results=test_results,
        )
    },

    {
        "widget_name": "memory - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('메모리')))",
        "element_name": "[>] button",
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.lomqVM",
        "button_name": "[>] button",
        "action":  lambda page, test_results: verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="리소스 이퀄라이저",
            expected_url="/dashboard/multi_line?content=memory"
        )
    },

    {
        "widget_name": "memory - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('메모리')))",
        "element_name": "PanelContents button",
        "element_locator": "{locator} .Ants__Dropdown-cCtpgz.bRdCUm",
        "button_name": "PanelContents button",
        "action": lambda page, test_results: dropdown_button_action(
            page=page,
            dropdown_locator="div.ant-dropdown.ant-dropdown-placement-bottomLeft",
            expected_left_value=947,
            test_results=test_results
        )
        
    },

    {
        "widget_name": "memory - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('메모리')))",
        "element_name": "PanelContents chart",
        "element_locator": "{locator} canvas.sc-dcJsrY.dvDjBb",
        "button_name": "PanelContents chart",
        "action": lambda page, test_results: (
            verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="서버 상세",
            expected_url="/server_detail"
        ),
            #verify_agent(page, expected_agent, test_results)
        ),
        "hover_positions": [  
        {"x":57,"y":44}
        ] # 툴팁 검증을 위한 좌표
    },

    {
        "widget_name": "memory - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('메모리')))",
        "element_name": "PanelContents dropdown",
        "element_locator": "{locator} .Ants__Dropdown-cCtpgz.bRdCUm",
        "button_name": "PanelContents dropdown",
        "action": lambda page, test_results: dropdown_button_action(
            page=page,
            dropdown_locator="div.ant-dropdown.ant-dropdown-placement-bottomLeft",
            expected_left_value=947,
            dropdown_list_button_locator='li:has-text("CPU")',
            element_locator="div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('expected_text'))) .Ants__Dropdown-cCtpgz.bRdCUm",
            expected_text="CPU",
            test_results=test_results
        )
        
    },


    {
        "widget_name": "disk I/O - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('디스크 I/O')))",
        "element_name": "info button",  
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.LPWtZ",
        "button_name": "info button",
        "action": lambda page, test_results: info_button_action(
            page=page,
            popover_locator="div.ant-popover.ant-popover-placement-top",  # Popover 부모 요소를 나타내는 조건
            popover_text_locator="div.HelperButton__ContentContainer-dPhKeC.eokXGu",  # 팝오버 텍스트 클래스
            expected_text="디스크 I/O",
            test_results=test_results,
        )
    },

    {
        "widget_name": "disk I/O - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('디스크 I/O')))",
        "element_name": "[>] button",
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.lomqVM",
        "button_name": "[>] button",
        "action":  lambda page, test_results: verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="리소스 이퀄라이저",
            expected_url="/dashboard/multi_line?content=diskio"
        )
    },

    {
        "widget_name": "disk I/O - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('디스크 I/O')))",
        "element_name": "PanelContents button",
        "element_locator": "{locator} .Ants__Dropdown-cCtpgz.bRdCUm",
        "button_name": "PanelContents button",
        "action": lambda page, test_results: dropdown_button_action(
            page=page,
            dropdown_locator="div.ant-dropdown.ant-dropdown-placement-bottomLeft",
            expected_left_value=947,
            test_results=test_results
        )
        
    },

    {
        "widget_name": "disk I/O - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('디스크 I/O')))",
        "element_name": "PanelContents chart",
        "element_locator": "{locator} canvas.sc-dcJsrY.dvDjBb",
        "button_name": "PanelContents chart",
        "action": lambda page, test_results: (
            verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="서버 상세",
            expected_url="/server_detail"
        ),
            #verify_agent(page, expected_agent, test_results)
        ),
        "hover_positions": [  
        {"x":62,"y":40}
        ] # 툴팁 검증을 위한 좌표
    },

    {
        "widget_name": "disk I/O - TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('디스크 I/O')))",
        "element_name": "PanelContents dropdown",
        "element_locator": "{locator} .Ants__Dropdown-cCtpgz.bRdCUm",
        "button_name": "PanelContents dropdown",
        "action": lambda page, test_results: dropdown_button_action(
            page=page,
            dropdown_locator="div.ant-dropdown.ant-dropdown-placement-bottomLeft",
            expected_left_value=947,
            dropdown_list_button_locator='li:has-text("CPU")',
            element_locator="div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(button.Styles__Button-bDBZvm:has(span:text('expected_text'))) .Ants__Dropdown-cCtpgz.bRdCUm",
            expected_text="CPU",
            test_results=test_results
        )
        
    },

    # {
    #     "widget_name": "Server Status Map",
    #     "locator": ".Styles__Panel-kJCnUy.iLiSQM",  # 위젯 자체 확인
    #     "element_name": "CPU Resource Map button",  
    #     "element_locator": ".Styles__Wrapper-bZXaBP.dfHBtW",
    #     "button_name": "CPU Resource Map button",
    #     "action": None
    # },

    # {
    #     "widget_name": "Server Status Map",
    #     "locator": ".Styles__FlexWrapper-fGKctw > div > .Styles__FlexWrapper-fGKctw > .Styles__FlexSizeWrapper-dheSQV",  # 위젯 자체 확인
    #     "element_name": "Server Status Map button",  
    #     "element_locator": ".Styles__Wrapper-bZXaBP.cgWROS",
    #     "button_name": "Server Status Map button",
    #     "action": None
    # },

    # {
    #     "widget_name": "Server Status Map",
    #     "locator": ".Styles__FlexWrapper-fGKctw > div > .Styles__FlexWrapper-fGKctw > .Styles__FlexSizeWrapper-dheSQV",  # 위젯 자체 확인
    #     "element_name": "Status Map chart",  
    #     "element_locator": "canvas.Honeycomb__CanvasDom-ecbovM.hbmIfB",
    #     "button_name": "Status Map chart",
    #     "action": lambda page, test_results: (
    #         verify_navigation_goback_action(
    #         page=page,
    #         test_results=test_results,
    #         screen_name="서버 상세",
    #         expected_url="/server_detail"
    #     ),
    #         #verify_agent(page, expected_agent, test_results)
    #     ),
    #     "hover_positions": [  
    #     {"x":347,"y":86}
    #     ] # 툴팁 검증을 위한 좌표
    # },

    {
        "widget_name": "프로세스 CPU TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 CPU TOP5'))",  # 위젯 자체 확인
        "element_name": "info button",  
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.LPWtZ",
        "button_name": "info button",
        "action": lambda page, test_results: processwidget_info_button_action(
            page=page,
            popover_locator="div.ant-popover.ant-popover-placement-top",  # Popover 부모 요소를 나타내는 조건
            popover_text_locator="div.HelperButton__ContentContainer-dPhKeC.eokXGu",  # 팝오버 텍스트 클래스
            expected_text="CPU",
            test_results=test_results,
        )
    },
    {
        "widget_name": "프로세스 CPU TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 CPU TOP5'))",  
        "element_name": "[>] button",  
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.lomqVM",
        "button_name": "[>] button",
        "action": lambda page, test_results: verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="프로세스 목록",
            expected_url="/process_list"
        )
    },
    {
        "widget_name": "프로세스 CPU TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 CPU TOP5'))",  
        "element_name": "process table",  
        "element_locator": "{locator} div.PanelContents__Body-ha-DReo.hssRVS",
        "button_name": None,
        "action": None
    },
    # info_button_action 함수 대신 column_button_action 함수 만들어서 사용해야함 스타일 요소가 -가 아닌 값을 찾는 조건 사용하기
    {
        "widget_name": "프로세스 CPU TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 CPU TOP5'))",
        "element_name": "process table name column",
        "element_locator": "{locator} tbody[role='rowgroup'] > tr[role='row']:nth-child(1) > td[role='cell']:nth-child(1)",
        "button_name": "process table name column",
        "action": lambda page, test_results: column_button_action(
            page=page,
            tooltip_locator="div.ant-tooltip.ant-tooltip-placement-top",  # tooltip 부모 요소를 나타내는 조건
            test_results=test_results
        )
        
    },
    {
        "widget_name": "프로세스 CPU TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 CPU TOP5'))",
        "element_name": "process table server column",
        "element_locator": "{locator} tbody[role='rowgroup'] > tr[role='row']:nth-child(1) > td[role='cell']:nth-child(5)",
        "button_name": "process table server column",
        "action": lambda page, test_results: column_button_action(
            page=page,
            tooltip_locator="div.ant-tooltip.ant-tooltip-placement-top",  # tooltip 부모 요소를 나타내는 조건
            test_results=test_results
        )
        
    },
    {
        "widget_name": "프로세스 메모리 TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 메모리 TOP5'))",  # 위젯 자체 확인
        "element_name": "info button",  
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.LPWtZ",
        "button_name": "info button",
        "action": lambda page, test_results: processwidget_info_button_action(
            page=page,
            popover_locator="div.ant-popover.ant-popover-placement-top",  # Popover 부모 요소를 나타내는 조건
            popover_text_locator="div.HelperButton__ContentContainer-dPhKeC.eokXGu",  # 팝오버 텍스트 클래스
            expected_text="메모리",
            test_results=test_results
        )
    },
    {
        "widget_name": "프로세스 메모리 TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 메모리 TOP5'))",  # 위젯 자체 확인
        "element_name": "[>] button",  
        "element_locator": "{locator} div.Styles__Wrapper-bZXaBP.lomqVM",
        "button_name": "[>] button",
        "action": lambda page, test_results: verify_navigation_action(
            page=page,
            test_results=test_results,
            screen_name="프로세스 목록",
            expected_url="/process_list"
        )
    },
    {
        "widget_name": "프로세스 메모리 TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 메모리 TOP5'))",  # 위젯 자체 확인
        "element_name": "process table",  
        "element_locator": "{locator} div.PanelContents__Body-ha-DReo.hssRVS",
        "button_name": None,
        "action": None
    },
    {
        "widget_name": "프로세스 메모리 TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 메모리 TOP5'))",
        "element_name": "process table name column",
        "element_locator": "{locator} tbody[role='rowgroup'] > tr[role='row']:nth-child(1) > td[role='cell']:nth-child(1)",
        "button_name": "process table name column",
        "action": lambda page, test_results: column_button_action(
            page=page,
            tooltip_locator="div.ant-tooltip.ant-tooltip-placement-top",  # tooltip 부모 요소를 나타내는 조건
            test_results=test_results
        )
        
    },
    {
        "widget_name": "프로세스 메모리 TOP5",
        "locator": "div.Styles__FlexSizeWrapper-dheSQV.dNazsF:has(span:text('프로세스 메모리 TOP5'))",
        "element_name": "process table server column",
        "element_locator": "{locator} tbody[role='rowgroup'] > tr[role='row']:nth-child(1) > td[role='cell']:nth-child(5)",
        "button_name": "process table server column",
        "action": lambda page, test_results: column_button_action(
            page=page,
            tooltip_locator="div.ant-tooltip.ant-tooltip-placement-top",  # tooltip 부모 요소를 나타내는 조건
            test_results=test_results
        )
        
    },

]