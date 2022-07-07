#吳倬安 508170624

# 解決不合法字元當檔案名
def replace(oriPath):
    title = oriPath.replace('/', ' ')
    title = title.replace('\\', ' ')
    title = title.replace('|', ' ')
    title = title.replace(':', ' ')
    title = title.replace('*', ' ')
    title = title.replace('?', ' ')
    title = title.replace('"', ' ')
    title = title.replace('<', ' ')
    title = title.replace('>', ' ')
    title = title.replace(';', ' ')
    title = title.replace(',', ' ')

    return title