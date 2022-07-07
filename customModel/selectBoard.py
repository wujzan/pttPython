#吳倬安 508170624

# lambda模擬switch,來選擇各個討論分板的網址
def links(userSelectBoard):
    return {
        0: lambda: "https://www.ptt.cc/bbs/movie/index.html",
        1: lambda: "https://www.ptt.cc/bbs/Stock/index.html",
        2: lambda: "https://www.ptt.cc/bbs/C_Chat/index.html",
        3: lambda: "https://www.ptt.cc/bbs/Tech_Job/index.html"
    }.get(userSelectBoard, lambda: "https://www.ptt.cc/bbs/movie/index.html")()