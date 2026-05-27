PS C:\Users\q00510847> welink-cli im query-recent-conversation --count 5
{
  "app_service_id": "1",
  "conversation_info": [
    {
      "cross_instance": false,
      "group_id": "0",
      "group_name": "",
      "group_type": "NORMAL_GROUP",
      "native_name": "张洋洋",
      "recent_conversation_type": "CHAT_TYPE_P2P_MSG",
      "staff_name": "zhangyangyang 00628533",
      "target_account": "z00628533"
    },
    {
      "cross_instance": false,
      "group_id": "944052726495445547",
      "group_name": "无线设计桌面模块内审",
      "group_type": "NORMAL_GROUP",
      "native_name": "",
      "recent_conversation_type": "CHAT_TYPE_GROUP_MSG",
      "staff_name": "",
      "target_account": ""
    },
    {
      "cross_instance": false,
      "group_id": "708543592267911909",
      "group_name": "工具二部团队建设群",
      "group_type": "NORMAL_GROUP",
      "native_name": "",
      "recent_conversation_type": "CHAT_TYPE_GROUP_MSG",
      "staff_name": "",
      "target_account": ""
    },
    {
      "cross_instance": false,
      "group_id": "717915662353219752",
      "group_name": "ALM&AI 2025全员",
      "group_type": "NORMAL_GROUP",
      "native_name": "",
      "recent_conversation_type": "CHAT_TYPE_GROUP_MSG",
      "staff_name": "",
      "target_account": ""
    },
    {
      "cross_instance": false,
      "group_id": "675805850476069040",
      "group_name": "ALM&AI 2025",
      "group_type": "NORMAL_GROUP",
      "native_name": "",
      "recent_conversation_type": "CHAT_TYPE_GROUP_MSG",
      "staff_name": "",
      "target_account": ""
    }
  ],
  "error": {
    "error_code": "IM.0000",
    "error_msg": "success"
  }
}

PS C:\Users\q00510847> welink-cli im query-history-message --query-count 5 --group-id 758559285016953862
{
  "respData": {
    "chatInfo": [
      {
        "at": false,
        "atAccountList": [],
        "content": "你好",
        "contentType": "TEXT_MSG",
        "groupId": 758559285016953862,
        "groupType": 0,
        "msgId": 88994507367466470,
        "receiver": "",
        "sender": "q00510847",
        "serverSendTime": 1779890147349
      },
      {
        "at": false,
        "atAccountList": [],
        "content": "没问题，请告诉我具体需要处理什么任务？比如整理数据、分析文本、编写代码，还是其他工作？请提供相关的背景信息或具体内容，我会立即开始处理。",
        "contentType": "TEXT_MSG",
        "groupId": 758559285016953862,
        "groupType": 0,
        "msgId": 88994507282518912,
        "receiver": "",
        "sender": "p_xiaoluban",
        "serverSendTime": 1779890145650
      },
      {
        "at": true,
        "atAccountList": [],
        "content": "@小鲁班 你来处理",
        "contentType": "TEXT_MSG",
        "groupId": 758559285016953862,
        "groupType": 0,
        "msgId": 88994507201164670,
        "receiver": "",
        "sender": "q00510847",
        "serverSendTime": 1779890144023
      },
      {
        "at": true,
        "atAccountList": [],
        "content": "@所有人 看下遗留事务",
        "contentType": "TEXT_MSG",
        "groupId": 758559285016953862,
        "groupType": 0,
        "msgId": 88994506916565723,
        "receiver": "",
        "sender": "q00510847",
        "serverSendTime": 1779890138331
      },
      {
        "at": true,
        "atAccountList": [],
        "content": "@小鲁班 ",
        "contentType": "TEXT_MSG",
        "groupId": 758559285016953862,
        "groupType": 0,
        "msgId": 88994485858685273,
        "receiver": "",
        "sender": "q00510847",
        "serverSendTime": 1779889717173
      }
    ],
    "maxMsgId": 88994507367466470,
    "minMsgId": 88994485858685273,
    "msgTotalCount": 5
  },
  "resultCode": "0",
  "resultContext": "Operate Success",
  "sno": null
}

PS C:\Users\q00510847> welink-cli im query-history-message --query-count 5 --user-account z00574872
{
  "respData": {
    "chatInfo": [
      {
        "at": false,
        "atAccountList": [],
        "content": "/:um_begin{https://clouddrive.huawei.com/f/1b38867ea1f317e62985dd64419dc7d6|File|38866|根据工号查询个人信息_Office2013版本.xlsm|0|;;2aeee5afcfc581345eb4|isOriginalImg: 0;md5:0105276ca802c57aad52a2591369a7c5;isCrossInstance:0;emotionId:;objectId:;cdnUrl:}/:um_end",
        "contentType": "FILE_MSG",
        "groupId": 0,
        "groupType": 0,
        "msgId": 88994439374270114,
        "receiver": "z00574872",
        "sender": "q00510847",
        "serverSendTime": 1779888787485
      },
      {
        "at": false,
        "atAccountList": [],
        "content": "/:um_begin{https://clouddrive.huawei.com/f/12d345c305bb41495579d8d113ff705b|Img|64141|14266633-D899-430F-B223-0FB89BB2E56E.gif|0|84;84;a9d3bcc2ae8dd43b8001|isOriginalImg: 0;md5:ef93e278efc35b26d0d27baf0af449fa;isCrossInstance:0;emotionId:;objectId:;cdnUrl:}/:um_end",
        "contentType": "PICTURE_MSG",
        "groupId": 0,
        "groupType": 0,
        "msgId": 88993299167705456,
        "receiver": "q00510847",
        "sender": "z00574872",
        "serverSendTime": 1779865983354
      },
      {
        "at": false,
        "atAccountList": [],
        "content": "吗的这玩意儿咋看",
        "contentType": "TEXT_MSG",
        "groupId": 0,
        "groupType": 0,
        "msgId": 88993297248093156,
        "receiver": "z00574872",
        "sender": "q00510847",
        "serverSendTime": 1779865944961
      },
      {
        "at": false,
        "atAccountList": [],
        "content": "怎么说，能看到不，走完没",
        "contentType": "TEXT_MSG",
        "groupId": 0,
        "groupType": 0,
        "msgId": 88993296782724423,
        "receiver": "q00510847",
        "sender": "z00574872",
        "serverSendTime": 1779865935654
      },
      {
        "at": false,
        "atAccountList": [],
        "content": "我看下",
        "contentType": "TEXT_MSG",
        "groupId": 0,
        "groupType": 0,
        "msgId": 88993279199417473,
        "receiver": "z00574872",
        "sender": "q00510847",
        "serverSendTime": 1779865583988
      }
    ],
    "maxMsgId": 88994439374270114,
    "minMsgId": 88993279199417473,
    "msgTotalCount": 5
  },
  "resultCode": "0",
  "resultContext": "Operate Success",
  "sno": null
}