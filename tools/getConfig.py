from tools.readFile import read_json_config


def getConfigInfo(target):
    config = read_json_config()  # 获取配置信息
    return config[target]
