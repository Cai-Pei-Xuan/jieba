# -*-coding:UTF-8 -*-
import jieba
import ijson
import json
import re
import jieba.posseg
import os
import time

# JSON轉換(string)
def JsonTransform(str):
    # Python 字典类型转换为 JSON 对象
    json_str = json.dumps(str)
    # print ("JSON 对象：", json_str)
    
    # 将 JSON 对象转换为 Python 字典
    data2 = json.loads(json_str)
    #print ("JSON 对象：", data2)
    return data2

# 删除列表中所有的空元素, 參考網站:https://blog.csdn.net/zziahgf/article/details/76199722
def DeleteNull(data):
    while '' in data:
        data.remove('')
    return data

# 處理data內的資料, 做分割(\n, ，, 。) 
def DealSplit(data):
    # re.split, 參考網站:https://blog.csdn.net/programmer_at/article/details/77409507
    dataList = re.split(r"[\n，。]", data)
    # print(data1)
    return dataList

# 读取数据，如果是用linux的話，建議還是用LoadJson()，ijson主要是為了省記憶體
def LoadJson_ijson(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        # ijson的用法，參考網站:https://www.ptt.cc/bbs/Python/M.1432703870.A.8D0.html
        arr = ijson.items(f, '')
        AllData = list(arr)
        AllData = AllData[0]
    return AllData

# 读取数据，
def LoadJson(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        AllData = json.load(f)
    return AllData

# 讀取常見詞或詞性列
def LoadCommonTable(filepath):
    CommonTable = []
    for i in open(filepath, 'r', encoding='UTF-8'):
        # 移除換行
        CommonTable.append(i.replace('\n', ''))
    return CommonTable

# 處理wikidata(做jieba)，並存檔(保留有用的詞彙)
def DealWikiData(path):
    # 讀檔路徑
    filepath = os.path.join(path, 'wiki20180805_fullText.json')
    # 引入繁體中文詞庫
    jieba.initialize(os.path.join(path, 'dict/dict.txt.big'))
    # 載入自訂的詞庫(可以多個載入，前面的資料會保留
    jieba.load_userdict(os.path.join(path, 'dict/mydict'))
    jieba.load_userdict(os.path.join(path, 'dict/dict.txt.big.txt'))
    jieba.load_userdict(os.path.join(path, 'dict/ptt.txt'))
    jieba.load_userdict(os.path.join(path, 'dict/wiki.dict.txt'))
    jieba.load_userdict(os.path.join(path, 'dict/attractions.dict.txt'))
    jieba.load_userdict(os.path.join(path, 'dict/dcard.dict.txt'))
    jieba.load_userdict(os.path.join(path, 'dict/zh_translate_en.dict'))
    # 自訂常見詞和詞性列
    CommonWordTable = LoadCommonTable(os.path.join(path, 'CommonTable/CommonWordTable'))
    # CommonPosTable = LoadCommonTable(os.path.join(path, 'CommonTable/CommonPosTable'))
    # 读取数据
    AllData = LoadJson(filepath)
    
    # 寫檔案+創建檔案：
    index = 0
    limit = 1000          # 每1000筆資料存一次檔
    while True:
        try :
            remainder = index//limit
            fileName = str(remainder) + '.txt'
            filepath = (os.path.join(path, 'AllCutWikiData/')) + fileName
            dataList = DealSplit(AllData[str(index)])      # 處理data內的資料, 做分割(\n, ，, 。)
            f = open(filepath, 'a', encoding = 'UTF-8')    # mode a，檔案存在，只寫開啟，追加內容 檔案不存在，則建立後，只寫開啟，追加內容
            # 讀取每一列資料
            for data in dataList:
                if data != '':
                    # 使用 jieba.posseg.lcut() 取得詞性
                    seg_list = jieba.posseg.lcut(data)
                    # 紀錄需要刪除的pair(因為有常見的詞性)
                    # for i in seg_list:
                    #     if not i.flag in CommonPosTable and not i.word in CommonWordTable:
                    #         f.write(i.word + ' ')       # 將詞彙寫入檔案

                    #只保留詞性是n和x的詞
                    for i in seg_list:
                        if i.flag == 'n' or i.flag == 'x':
                            if not i.word in CommonWordTable:
                                f.write(i.word + ' ')       # 將詞彙寫入檔案

                    f.write('\n')                       #換行
                    
            f.close()
            index += 1
        except :
            break

# 統計所有關鍵詞的詞頻表
def StatisticsWordFrequencyTable(path):
    # 统计文件夹下文件的数目，參考網站:https://blog.csdn.net/Engineer_X/article/details/80295884
    DIR = path + '/AllCutWikiData' #要统计的文件夹
    #print (len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]))
    num = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])

    # AllCutWikiData底下所有的資料做關鍵詞的關聯度排行列表
    # dictionary (字典) 基本指令，參考網站:http://design2u.me/blog/33/python-list-%E4%B8%B2%E5%88%97-%E8%88%87-dictionary-%E5%AD%97%E5%85%B8-%E5%9F%BA%E6%9C%AC%E6%8C%87%E4%BB%A4
    # Dict大概會存成這樣，Dict = {"a" : 3, "b" : 1, "c" : 2}
    Dict = {}
    for i in range(num):
        # 讀檔(處理過wikidata後的詞彙資料)
        filepath = path + '/AllCutWikiData/' + str(i) + '.txt'
        for j in open(filepath, 'r', encoding='UTF-8'):
            # 移除換行，並用空格分割
            dataList = []
            dataList = j.replace('\n', '').split(' ')
            for key_A in dataList:
                if key_A != '':
                    # 如果沒有在字典內就建一個
                    if key_A not in Dict.keys():
                        Dict[key_A] = 1
                    else :
                        Dict[key_A] = Dict[key_A] + 1
            dataList.clear()
           
    # 字典排序，參考網站:https://segmentfault.com/a/1190000004959880 or https://blog.csdn.net/xuezhangjun0121/article/details/78477028
    # sort_Dict = {}
    # sort_key = sorted(Dict.items(), key=lambda d: d[1], reverse=True)
    # sort_Dict = sort_key
    # print(sort_key)

    # 將字典存檔，字典快速保存與读取，參考網站:https://blog.csdn.net/u012155582/article/details/78077180
    filepath = path + '/WordFrequency/AllKeyWordFrequency.json'
    f = open(filepath, 'w', encoding='UTF-8')
    json.dump(Dict,f, ensure_ascii=False)
    f.close()

# 統計與所有關鍵詞的關聯度排行表
def StatisticsRankingTable(path):
    # 统计文件夹下文件的数目，參考網站:https://blog.csdn.net/Engineer_X/article/details/80295884
    DIR = path + '/AllCutWikiData' #要统计的文件夹
    #print (len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]))
    num = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])

    # AllCutWikiData底下所有的資料做關鍵詞的關聯度排行列表
    #　dictionary (字典) 基本指令，參考網站:http://design2u.me/blog/33/python-list-%E4%B8%B2%E5%88%97-%E8%88%87-dictionary-%E5%AD%97%E5%85%B8-%E5%9F%BA%E6%9C%AC%E6%8C%87%E4%BB%A4
    # Dict大概會存成這樣，Dict = {"a" : {"s" : 1, "b" : 2}, "n" : {"s" : 3, "b" : 4}}
    Dict = {}
    for i in range(num):
        # 讀檔(處理過wikidata後的詞彙資料)
        filepath = path + '/AllCutWikiData/' + str(i) + '.txt'
        for j in open(filepath, 'r', encoding='UTF-8'):
            # 移除換行，並用空格分割
            dataList = []
            dataList = j.replace('\n', '').split(' ')
            for key_A in dataList:
                if key_A != '':
                    # 如果沒有在字典內就建一個
                    if key_A not in Dict.keys():
                        Dict[key_A] = {}
                    for Key_B in dataList:
                        if key_A != Key_B and Key_B != '':
                            # 如果沒有在字典內就建一個，並給值
                            if Key_B not in Dict[key_A].keys():
                                Dict[key_A][Key_B] = 1
                            else:
                                Dict[key_A][Key_B] += 1
            dataList.clear()
           
    # 字典排序，參考網站:https://segmentfault.com/a/1190000004959880 or https://blog.csdn.net/xuezhangjun0121/article/details/78477028
    sort_Dict = {}
    for d_key in Dict.keys():
        sort_key = sorted(Dict[d_key].items(), key=lambda d: d[1], reverse=True)
        sort_Dict[d_key] = sort_key
        # print(sort_key)

    # 將字典存檔，字典快速保存與读取，參考網站:https://blog.csdn.net/u012155582/article/details/78077180
    filepath = path + '/StatisticsRanking/AllKeyWord.json'
    f = open(filepath, 'w', encoding='UTF-8')
    json.dump(sort_Dict,f)
    f.close()

# 統計所有關鍵詞的相似度(由兩者的關聯度表中前X筆共同的詞彙數量決定)排行表
def WordSimilarRankingTable(path):
    # 讀檔(所有關鍵字的關聯度表)
    filepath = path + '/StatisticsRanking/AllKeyWord.json'
    f = open(filepath, 'r', encoding='UTF-8')
    Dict = json.load(f)
    f.close()

    # SimilarDict大概會存成這樣，SimilarDict = {"a" : {"s" : 1, "b" : 2}, "n" : {"s" : 3, "b" : 4}}
    SimilarDict = {}        # 所有關鍵詞的相似度排行表的字典
    # 做所有關鍵詞的相似度
    for d_key in Dict.keys():
        SimilarDict[d_key] = {}     # 關鍵詞的相似度排行表的字典
        SimilarCandidate = []   #相似詞候補
        num_A = 0

        # 從關鍵詞的關聯度找到其他關鍵詞
        for k_A, v_A in Dict[d_key]:
            if num_A < 10:
                num_B = 0
                for k_B, v_B in Dict[k_A]:
                    if num_B < 10:
                        if k_B not in SimilarCandidate:
                            SimilarCandidate.append(k_B)
                            num_B += 1

                num_A += 1
                # 檢查當取了10個關聯度時，SimilarCandidate還是少於10個時，就繼續找下一個關聯度
                if num_A == 10:
                    if len(SimilarCandidate) < 10:
                        num_A -= 1
        
        # 取出關鍵詞的前10個關聯度
        num = 0
        list_A = []
        for k_A, v_A in Dict[d_key]:
            if num < 10:
                list_A.append(k_A)
                num += 1
        set_A = set(list_A)

        # 將關鍵詞與所有候補關鍵詞，比對各自前10個關聯度
        for Candidate in SimilarCandidate:
            # 取出候補關鍵詞的前10個關聯度
            num = 0
            list_B = []
            for k_B, v_B in Dict[Candidate]:
                if num < 10:
                    list_B.append(k_B)
                    num += 1
            set_B = set(list_B)

            # 比對各自前10個關聯度
            # 找出两个list中的相同元素，參考網站:https://zhidao.baidu.com/question/327705051776436045.html
            # 兩個List的交集數量
            leng = len(set_A & set_B)
            SimilarDict[d_key][Candidate] = leng    # 給關鍵詞的相似度數值(交集數量)
            list_B.clear()
            
        # 將關鍵詞的相似度排行表做排序(大到小)
        SimilarDict[d_key] = sorted(SimilarDict[d_key].items(), key=lambda d: d[1], reverse=True)

        SimilarCandidate.clear()
        list_A.clear()

    # 將字典存檔
    filepath = path + '/WordSimilarRanking/AllKeyWordSimilar.json'
    f = open(filepath, 'w', encoding='UTF-8')
    json.dump(SimilarDict,f)
    f.close()

# 查詢關鍵詞的關聯度
def InquireKeyWordConnection(Dict):
    judge = 1
    while judge == 1:
        name = input('請輸入你要查詢的關鍵詞：')
        if name in Dict.keys():
            num = 10    # 前10筆資料
            for data in Dict[name]:
                if num != 0:
                    print(data)
                    num -= 1
        else:
            print('沒有該詞的資料')

        s = input('請決定是否要繼續查詢(1代表繼續)：')
        if s != '1':
            judge = 0

# 查詢關鍵詞的相似度
def InquireKeyWordSimilar(Dict):
    judge = 1
    while judge == 1:
        name = input('請輸入你要查詢的關鍵詞：')
        if name in Dict.keys():
            num = 10    # 前10筆資料
            for data in Dict[name]:
                if num != 0:
                    # 當初建字典時忘記排除相同的詞
                    if not name in data:
                        print(data)
                        num -= 1
        else:
            print('沒有該詞的資料')

        s = input('請決定是否要繼續查詢(1代表繼續)：')
        if s != '1':
            judge = 0

if __name__ == '__main__':

    # start = time.time()
    path = os.getcwd()  # 當前路徑

    ###建立所需的資料---
    # 處理wikidata(做jieba)，並存檔(保留有用的詞彙)
    # DealWikiData(path)
    # 統計所有關鍵詞的詞頻表
    # StatisticsWordFrequencyTable(path)
    # 統計所有關鍵詞的關聯度排行表
    # StatisticsRankingTable(path)
    # 統計所有關鍵詞的相似度排行表
    # WordSimilarRankingTable(path)
    ###---

    ###字典載入---
    # 關聯度字典
    Connection_dict = LoadJson(path + '/StatisticsRanking/AllKeyWord.json')
    # 相似度字典   
    Similar_dict =  LoadJson(path + '/WordSimilarRanking/AllKeyWordSimilar.json')
    ###---

    judge = 1
    while judge == 1:
        function = input('請輸入你要的功能(1:代表查詢關鍵詞的關聯度，2:代表查詢關鍵詞的相似度，任意值:結束功能)：')
        if function == '1':
            InquireKeyWordConnection(Connection_dict)
        elif function == '2':
            InquireKeyWordSimilar(Similar_dict)
        else:
            judge = 0
 

    # end = time.time()
    # elapsed = end - start
    # print ("Time taken: " + str(elapsed) + "seconds.")

    
    
# data1 = {"0": "數學\n數學是利用符號語言研究數量、結構、變化以及空間等概念的一門學科，從某種角度看屬於形式科學的一種。\n"}
# data2 = JsonTransform(data1)
# data3 = DealSplit(data2['0'])
# for data in data3:
#     if data != '':
#         # 使用 jieba.posseg.lcut() 取得詞性
#         seg_list = jieba.posseg.lcut(data)
#         print(seg_list)
    
