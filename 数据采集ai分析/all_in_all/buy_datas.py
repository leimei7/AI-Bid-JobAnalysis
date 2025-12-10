from bs4 import BeautifulSoup


def extract_targets(html_content):
    # 初始化返回值为两个空字符串
    result = ["", ""]

    if html_content is None:
        return result  # 提取失败时返回["", ""]

    # 处理Tag对象，转换为HTML字符串
    if hasattr(html_content, 'prettify'):
        html_content = html_content.prettify()

    soup = BeautifulSoup(html_content, 'html.parser')
    breadcrumb_container = soup.find('div', class_='vF_deail_currentloc')

    if not breadcrumb_container:
        return result

    a_tags = breadcrumb_container.find_all('a', class_='CurrChnlCls')
    # 确保至少有2个标签才提取（避免索引越界）
    if len(a_tags) >= 2:
        result[0] = a_tags[-2].get_text(strip=True)  # 地方公告
        result[1] = a_tags[-1].get_text(strip=True)  # 中标公告

    return result

def extract_content(html_content):
    """
    从 HTML 内容中提取政府采购中标公告的关键信息

    Args:
        html_content (str): HTML 内容字符串

    Returns:
        dict: 提取的结构化数据
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 提取页面标题
    title = soup.title.string.strip() if soup.title else ""

    # 提取公告发布时间
    pub_time_elem = soup.select_one('#pubTime')
    pub_time = pub_time_elem.text.strip() if pub_time_elem else ""

    # 提取核心内容区域（使用更通用的选择器）
    content_div = soup.select_one('div[class^="vF_detail_main"]')
    if not content_div:
        print("未找到内容区域")
        return None

    title_div = soup.select_one('div[class^="vF_deail_currentloc"]')
    gg = extract_targets(str(title_div))
    if not title_div:
        print("未找到内容区域")
        return None

    soup = BeautifulSoup(content_div.text, 'html.parser')
    pure_text = soup.get_text()

    # 清理多余空白（可选）
    pure_text = ' '.join(pure_text.split())
    area_type = f"bidSort:{gg[0]},type:{gg[1]},"
    pure_text =  area_type + pure_text

    return pure_text

def extract_content_test():
    html_content = """
       <!doctype html>
           <html>
           <head>
           <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
           <meta http-equiv="pragma" content="no-cache">
           <meta http-equiv="cache-control" content="no-cache">
           <meta http-equiv="expires" content="0">
           <meta name="SiteName" content="中国政府采购网" />
           <meta name="SiteDomain" content="www.ccgp.gov.cn" />
           <meta name="SiteIDCode" content="bm14000002" />
           <meta name="ArticleTitle" content="清镇市2025年农村综合改革转移支付预算（农村公益事业财政奖补）项目麦格苗族布依族乡太阳能路灯采购的中标(成交)结果公告" />
           <meta name="PubDate" content="2025-06-27 17:52" />
           <meta name="ContentSource" content="中国政府采购网" />
           <title>清镇市2025年农村综合改革转移支付预算（农村公益事业财政奖补）项目麦格苗族布依族乡太阳能路灯采购的中标(成交)结果公告</title>
           <link href="/css/detail.css" rel="stylesheet" type="text/css" />
           <script language="javascript" src="/js/jquery-3.2.1.min.js"></script>
           <script language="javascript" src="//pub.ccgp.gov.cn/common/js/jquery.qrcode.min.js"></script>
           </head>
           <body id="detail"><script id="keyparam" src="/_bot_sbu/sbu_fpcm.js">b220cb5b51b0940c0f343d37ebb48744</script><script id="keyt" src="/_bot_sbu/sbu_fpc.js">900</script><script>(function () { document.cookie = "HOY_TR=IENBCJGQSPTMWXHY,567142A8B9CDEF03,psgtfrzwjdkhblim; max-age=31536000; path=/";document.cookie = "HBB_HC=de65b0eb0fa18cfa2d87a627d4daaf089e273d4f4886cb623858569b3188378128443fe87ab9c78f7450415e45c16292af; max-age=600; path=/"; })()</script><script src="/_ws_sbu/sbu_hc.js"></script>
           <link href="//www.ccgp.gov.cn/css/inc.css" rel="stylesheet" type="text/css" />
           <div class="v4incheadertop">
               <div class="v4incheadertop_tel_block">
                   <div class="v4incheadertop_tel">
                       <p class="cl">财政部唯一指定政府采购信息网络发布媒体 国家级政府采购专业网站</p><p class="cr">服务热线：400-810-1996</p>
                   </div>
               </div>
               <div class="v4incheadertop_logosearch_block2">
                   <div class="v4incheadertop_logosearch">
                   <div class="searcharea1">
                       <div class="logo_gh" style="margin-top:20px">
                       <a href="#" class="ccgp"></a>
                       <a href="#" class="ccgp2"></a>
                       <a href="#" class="gmfw"></a>
                       <a href="#" class="ccgp3"></a>
                       </div>
                   </div>

                   <div class="searcharea2">
                       <div class="sangong_bl"></div>

                   </div></div>
               </div>
               <div class="v4incheadertop_nav_block">
                   <div class="v4incheadertop_nav">
                       <ul class="v4incheadertop_nav_ls">
                           <li  id="ch_index" style="width:140px"><a href="//www.ccgp.gov.cn/">首页</a></li>
                           <li id="ch_zcfg" style="width: 172px"><a href="//www.ccgp.gov.cn/zcfg/">政采法规</a></li>
                           <li id="ch_gmfw" style="width:172px"><a href="//www.ccgp.gov.cn/gpsr/">购买服务</a></li>
                           <li id="ch_jdjc" style="width:172px"><a href="//www.ccgp.gov.cn/jdjc/">监督检查</a></li>
                           <li id="ch_xxgg" style="width:172px"><a href="//www.ccgp.gov.cn/xxgg/">信息公告</a></li>
                           <li id="ch_gpa" style="width:172px"><a href="//www.ccgp.gov.cn/wtogpa/">国际专栏</a></li>
                       </ul>
                   </div>
               </div>
               <div class="clb"></div>
           </div>

           <div class="main">
           <div class="main_container">




               <div class="vF_deail_currentloc mt10">
                   <p>当前位置：<a href="../../../../" title="首页" class="CurrChnlCls">首页</a>&nbsp;&raquo;&nbsp;
                           <a href="../../../" title="政采公告" class="CurrChnlCls">政采公告</a>&nbsp;&raquo;&nbsp;<a href="../../" title="地方公告" class="CurrChnlCls">地方公告</a>&nbsp;&raquo;&nbsp;<a href="../" title="中标公告" class="CurrChnlCls">中标公告</a></p>
               </div>
               <div class="vF_deail_maincontent">

           <div class="vF_detail_main  pzln52gui">
                       <div class="vF_detail_header"><h2 class="tc">清镇市2025年农村综合改革转移支付预算（农村公益事业财政奖补）项目麦格苗族布依族乡太阳能路灯采购的中标(成交)结果公告</h2>
                       <p class="tc"><span id="pubTime">2025年06月27日 17:52</span> 来源：<span id="sourceName"></span> 【<span id="printBtn">打印</span>】 <span id="shareTo"></span></p></div>
           <!--contentTable-->
           <div class='table'><h5>公告概要：</h5><table width='600' border='0' cellspacing='1' bgcolor='#bfbfbf' style='text-align:left;'><tr><td colspan='4'><b>公告信息：</b></td></tr><tr><td class='title' width='128'>采购项目名称</td><td colspan='3' width='430'>清镇市2025年农村综合改革转移支付预算（农村公益事业财政奖补）项目麦格苗族布依族乡太阳能路灯采购</td></tr><tr><td class='title'>品目</td><td colspan='3'><p></p></td></tr><tr><td class='title'>采购单位</td><td colspan='3'>清镇市麦格苗族布依族乡人民政府</td></tr><tr><td class='title'>行政区域</td><td width='168'>贵州省</td><td class='title' width='128'>公告时间</td><td width='168'>2025年06月27日  17:52</td></tr><tr><td class='title'>评审专家名单</td><td colspan='3'>赵有亮、叶华、邓霁</td></tr><tr><td class='title'>总中标金额</td><td colspan='3'>￥56.980000 万元（人民币）</td></tr><tr><td colspan="4"><b>联系人及联系方式：</b></td></tr><tr><td class='title'>项目联系人</td><td colspan='3'>朱元杰、陈丽、刘松</td></tr><tr><td class='title'>项目联系电话</td><td colspan='3'>18585427887</td></tr><tr><td class='title' width='128'>采购单位</td><td width='430' colspan='3'>清镇市麦格苗族布依族乡人民政府</td></tr><tr><td class='title'>采购单位地址</td><td colspan='3'>清镇市麦格乡麦格村黄兴寨组</td></tr><tr><td class='title'>采购单位联系方式</td><td colspan='3'>13984083455</td></tr><tr><td class='title'>代理机构名称</td><td colspan='3'>贵州励柯工程咨询有限公司</td></tr><tr><td class='title'>代理机构地址</td><td colspan='3'>贵州省贵阳市观山湖区金华园街道金阳烈变国际广场(A)1单元16楼1号</td></tr><tr><td class='title'>代理机构联系方式</td><td colspan='3'>18585427887</td></tr></table></div>
           <!--contentTable-->
           <div class="vF_detail_content_container">
                       <div class="vF_detail_content">
                           <style id="fixTableStyle" type="text/css">th,td {border:1px solid #DDD;padding: 5px 10px;}</style>  <p style="line-height: normal; text-align: justify;"><strong style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; text-align: justify;">一、项目编号：</strong><samp style="font-family: inherit" class="bookmark-item uuid-1650446712230 code-00004 addWord single-line-text-input-box-cls">LKZX2025-CG013</samp></p>  <p style="margin: 17px 0px; text-align: justify; break-after: avoid; font-size: 18px; font-family: SimHei, sans-serif; white-space: normal; line-height: normal;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"><strong style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; text-align: justify; white-space: normal;">二、项目名称：</strong><span class="bookmark-item uuid-1591615489941 code-00003 addWord single-line-text-input-box-cls">清镇市2025年农村综合改革转移支付预算（农村公益事业财政奖补）项目麦格苗族布依族乡太阳能路灯采购</span></span></p>  <p style="margin-bottom: 15px; line-height: normal;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"><strong>三、中标（成交）信息</strong> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</span></p>  <div style=" font-size:16px;  font-family:微软雅黑;  line-height:20px; ">   <p style="line-height: normal; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;">1.中标结果： &nbsp; &nbsp;</span>&nbsp; &nbsp; &nbsp;<span style="text-indent: 2em;">&nbsp;</span> &nbsp; &nbsp;</p>   <div class="class-condition-filter-block">    <table class="template-bookmark uuid-1714974088559 code-AM014zbcj0001 text-中标/成交结果信息-最低评标价法" style="width: 100%; border-collapse:collapse;">     <thead>      <tr style="text-align: center;" class="firstRow">       <td style="background-color: #fff;"><strong>序号</strong></td>       <td style="background-color: #fff;"><strong>供应商名称</strong></td>       <td style="background-color: #fff;"><strong>供应商地址</strong></td>       <td style="background-color: #fff;"><strong>中标（成交）金额</strong></td>       <td style="background-color: #fff;"><strong>评审报价</strong></td>      </tr>     </thead>     <tbody replace="true">     <tr replace="true">      <td style="font-size: 14px;font-family: 微软雅黑, 'Microsoft YaHei';" class="code-sectionNo" align="center" valign="middle">1</td>      <td style="font-size: 14px;font-family: 微软雅黑, 'Microsoft YaHei';" class="code-winningSupplierName" align="center" valign="middle">江苏新煦光电科技有限公司</td>      <td style="font-size: 14px;font-family: 微软雅黑, 'Microsoft YaHei';" class="code-winningSupplierAddr" align="center" valign="middle">高邮市菱塘工业集中区</td>      <td style="font-size: 14px;font-family: 微软雅黑, 'Microsoft YaHei';" class="code-summaryPrice" align="center" valign="middle">总价形式报价:569800.00(元)</td>      <td style="font-size: 14px;font-family: 微软雅黑, 'Microsoft YaHei';" class="code-supplierReviewPrice" align="center" valign="middle">-</td>     </tr>    </tbody>    </table>   </div>  </div>  <p style="margin: 17px 0px; text-align: justify; break-after: avoid; font-size: 16px; font-family: SimHei, sans-serif; white-space: normal; line-height: normal;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"><strong>四、主要标的信息</strong> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</span> &nbsp; &nbsp; &nbsp; &nbsp;</p>  <div style=" font-size:16px;  font-family:微软雅黑;  line-height:20px;">   <div class="class-condition-filter-block">    <p style="line-height: normal;"><span style="font-size: 16px;">&nbsp; &nbsp;货物类主要标的信息：</span> &nbsp; &nbsp;</p>    <p style="line-height: normal;" class="sub">&nbsp; &nbsp;&nbsp;<span class="bookmark-item uuid-1589437802153 code-AM014GoodsInfoTab  addWord">     <table class="form-panel-input-cls" width="100%">      <tr width="100%" style="text-align: center;">       <td width="14.29%" style="word-break:break-all;">序号</td>       <td width="14.29%" style="word-break:break-all;">标项名称</td>       <td width="14.29%" style="word-break:break-all;">标的名称</td>       <td width="14.29%" style="word-break:break-all;">品牌</td>       <td width="14.29%" style="word-break:break-all;">规格型号</td>       <td width="14.29%" style="word-break:break-all;">数量</td>       <td width="14.29%" style="word-break:break-all;" colSpan="1">单价（元）</td>      </tr>      <tr width="100%" style="text-align: center;">       <td width="14.29%" style="word-break:break-all;">1</td>       <td width="14.29%" style="word-break:break-all;">清镇市2025年农村综合改革转移支付预算（农村公益事业财政奖补）项目麦格苗族布依族乡太阳能路灯采购</td>       <td width="14.29%" style="word-break:break-all;">清镇市2025年农村综合改革转移支付预算（农村公益事业财政奖补）项目麦格苗族布依族乡太阳能路灯采购</td>       <td width="14.29%" style="word-break:break-all;">详见附件</td>       <td width="14.29%" style="word-break:break-all;">详见附件</td>       <td width="14.29%" style="word-break:break-all;">1</td>       <td width="14.29%" style="word-break:break-all;" colSpan="1">569800</td>      </tr>     </table></span>&nbsp;</p>   </div>  </div>  <p style="margin: 17px 0px; text-align: justify; break-after: avoid; font-size: 16px; font-family: SimHei, sans-serif; white-space: normal; line-height: normal;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"><strong>五、评审专家（单一来源采购人员）名单：</strong> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</span></p>  <p style="line-height: normal; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"><span style="line-height: 20px; font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"><span class="bookmark-item uuid-1589193390811 code-85005 addWord multi-line-text-input-box-cls">赵有亮、叶华、邓霁</span>&nbsp;</span> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</span></p>  <p style="margin: 17px 0px; text-align: justify; break-after: avoid; font-size: 16px; font-family: SimHei, sans-serif; white-space: normal; line-height: normal;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"><strong>六、代理服务收费标准及金额：</strong>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</span></p>  <p style="line-height: normal; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"><span style="line-height: 20px; font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;">1.代理服务收费标准：<span class="bookmark-item uuid-1591615554332 code-AM01400039 addWord multi-line-text-input-box-cls">本项目代理服务费由中标供应商向采购代理机构一次性支付，代理服务费为包干价人民币捌仟贰佰元整。</span>&nbsp;</span> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</span></p>  <p style="line-height: normal; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"><span style="line-height: 20px; font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;">2.代理服务收费金额（元）：<span class="bookmark-item uuid-1591615558580 code-AM01400040 addWord numeric-input-box-cls readonly">8200</span>&nbsp;</span>&nbsp;</span></p>  <p style="margin: 17px 0px; text-align: justify; break-after: avoid; font-size: 16px; font-family: SimHei, sans-serif; white-space: normal; line-height: normal;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"><strong>七、公告期限</strong> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</span></p>  <p style="line-height: normal; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"><span style="line-height: 20px; font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;">自本公告发布之日起1个工作日。</span> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</span></p>  <p style="margin: 17px 0px; text-align: justify; break-after: avoid; font-family: SimHei, sans-serif; white-space: normal; line-height: normal;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"><strong>八、其他补充事宜</strong>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</span></p>  <p style="line-height: normal; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"><span style="line-height: 20px; font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"><span class="bookmark-item uuid-1592539159169 code-81205 addWord multi-line-text-input-box-cls">/</span>&nbsp;</span>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</span></p>  <p style="margin: 17px 0px; text-align: justify; break-after: avoid; font-size: 16px; font-family: SimHei, sans-serif; white-space: normal; line-height: normal;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"><strong>九、对本次公告内容提出询问，请按以下方式联系</strong>　　　&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</span></p>  <p style="line-height: normal;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 16px;"></span></p>  <div style="white-space: normal; font-family: 微软雅黑; line-height: 30px;">   <div style="line-height: 30px;">    <p style="line-height: 1.5em; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;;">1.采购人信息</span> &nbsp; &nbsp; &nbsp; &nbsp;</p>    <p style="line-height: normal; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;;">名 称：<span class="bookmark-item uuid-1596004663203 code-00014 editDisable interval-text-box-cls readonly">清镇市麦格苗族布依族乡人民政府</span></span> &nbsp; &nbsp; &nbsp; &nbsp;</p>    <p style="line-height: normal; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;;">地 址：<span class="bookmark-item uuid-1596004672274 code-00018 addWord single-line-text-input-box-cls">清镇市麦格乡麦格村黄兴寨组</span></span> &nbsp; &nbsp; &nbsp; &nbsp;</p>    <p style="line-height: normal; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;;">联系方式：<span class="bookmark-item uuid-1596004695990 code-00016 editDisable single-line-text-input-box-cls readonly">13984083455</span></span> &nbsp; &nbsp; &nbsp; &nbsp;</p>    <p style="line-height: 1.5em; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;;">2.采购代理机构信息</span> &nbsp; &nbsp; &nbsp; &nbsp;</p>    <p style="line-height: normal; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;;">名 称：<span class="bookmark-item uuid-1596004721081 code-00009 addWord interval-text-box-cls">贵州励柯工程咨询有限公司</span></span> &nbsp; &nbsp; &nbsp; &nbsp;</p>    <p style="line-height: normal; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;;">地 址：<span class="bookmark-item uuid-1596004728442 code-00013 editDisable single-line-text-input-box-cls readonly">贵州省贵阳市观山湖区金华园街道金阳烈变国际广场(A)1单元16楼1号</span></span> &nbsp; &nbsp; &nbsp; &nbsp;</p>    <p style="line-height: normal; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;;">联系方式：<span class="bookmark-item uuid-1596004753055 code-00011 addWord single-line-text-input-box-cls">18585427887</span></span> &nbsp; &nbsp; &nbsp; &nbsp;</p>   </div>  </div>  <p style="line-height: 1.5em; white-space: normal; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;;">3.项目联系方式</span></p>  <p style="line-height: 1.5em; white-space: normal; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;;">项目联系人：<samp class="bookmark-item uuid-1650445786340 code-00010 editDisable single-line-text-input-box-cls readonly" style="font-family: inherit;">朱元杰、陈丽、刘松</samp></span></p>  <p style="line-height: 1.5em; white-space: normal; text-indent: 2em;"><span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;;">电 话：<samp class="bookmark-item uuid-1650445795121 code-00011 addWord single-line-text-input-box-cls" style="font-family: inherit;">18585427887</samp></span></p>  <p style="line-height: normal;">&nbsp;</p>  <blockquote style="display: none;">   <samp style="font-family: inherit; background-color: rgb(247, 247, 247); color: rgb(27, 120, 255);" class="bookmark-item uuid-1714974107532 code-biddingTableEl editDisable single-line-text-input-box-cls readonly">0</samp>  </blockquote>  <p>&nbsp;</p>  <p><br/></p>  <p><br/></p>  <p><br/></p>  <p><br/></p>  <p><br/></p>  <p><br/></p>  <p><br/></p>  <p><br/></p>  <p><br/></p>  <p><br/></p> </div><p style='font-size' class='fjxx'>附件信息：</p><ul class="fjxx" style="font-size: 16px;margin-left: 38px;color: #0065ef;list-style-type: none"><li><p style="display:inline-block"><a href="https://gz-gov-open-doc.oss-cn-gz-ysgzlt-d01-a.ltops.gzdata.com.cn/1024FPA/open/712f2f61-2276-466e-9e97-677c77b8e3bc.pdf" ignore=1>中标（成交）结果公告.pdf</a></p></li><li><p style="display:inline-block"><a href="https://gz-gov-open-doc.oss-cn-gz-ysgzlt-d01-a.ltops.gzdata.com.cn/1024FPA/open/0c69a8f3-9fff-4753-afda-89ef8780ecb8.zip" ignore=1>中标结果文件压缩包.zip</a></p></li>
                       </div>
                   </div><!--vF_detail_content_container-->
                   </div><!--vF_detail_main-->


               </div><!--vF_deail_maincontent-->
               <div class="vF_detail_relcontent mt13">
               <h2><p>相关公告</p></h2>
               <div class="vF_detail_relcontent_lst">
                   <ul class="c_list_tat">

                   </ul>
               </div>
           </div><!--相关公告-->

               </div>
           </div>
           </div>
           <div class="footer mt13">

               <div class="copyright_bl">
           <style type="text/css">
               .copyright_bl{width:1000px;margin:0 auto}/*margin-top:20px;*/
               .vF_cp {width: 1000px;margin: 0 auto;text-align: left;float: left;background: #e9e9e9;color: #333;height: 120px;padding-top: 10px;}
               .vF_cp p {width: 600px;float: left;margin-top: 15px;font-size: 14px;line-height: 26px;}
               .vF_cp span{font-family:Verdana, Geneva, sans-serif;font-size:12px}
               .vF_cp a,.vT_cp a{color:#333;text-decoration: none}
               .vF_cp a:hover,.vT_cp a:hover{text-decoration: underline;color:#ba2636}
               .dzjg {width: 205px;height: 80px;float: left;margin: 14px 10px 0 130px;border-right: 1px solid #c2c2c2;}
               .cpright {float: left;width: 570px;margin-left: 15px;}
               .ccgpjiucuo{width:110px;height:55px;float:left;margin-left:5px;margin-top:10px}
               @media print {.main_container{float:left}}
               </style>
                <div class="vF_cp">
                   <div class="dzjg">
                       <div class="ccgpjiucuo">
                           <a href="https://zfwzgl.www.gov.cn/exposure/jiucuo.html?site_code=bm14000002&amp;url=http%3A%2F%2Fwww.ccgp.gov.cn%2F" target="_blank"><img src="//www.ccgp.gov.cn/img/jiucuo.png"></a>
                           </div>
                       <script type="text/javascript">document.write(unescape("%3Cspan id='_ideConac' %3E%3C/span%3E%3Cscript src='https://dcs.conac.cn/js/33/000/0000/60425889/CA330000000604258890010.js' type='text/javascript'%3E%3C/script%3E"));</script></div>
               <div class="cpright">
                   <p>
                   主办单位：中华人民共和国财政部国库司  <br>网站标识码：<span>bm14000002</span> &nbsp;|&nbsp; <a href="https://beian.miit.gov.cn" target="_blank">京<span>ICP</span>备<span>19054529</span>号<span>-1</span></a> &nbsp;|&nbsp; 京公网安备<span>11010602060068</span>号 <br><span id="botm_cpy">&copy; 1999-</span> 中华人民共和国财政部 版权所有 &nbsp;|&nbsp; <a href="/contact.shtml" target="_blank">联系我们</a> &nbsp;|&nbsp; <a href="//www.ccgp.gov.cn/zxly/" target="_blank">意见反馈</a> </p>
               </div>
               </div>
               </div>
               <script language="javascript">
                   var myDate = new Date();
                   var botmcpy='&copy; 1999-'+ myDate.getFullYear();
                   $("#botm_cpy").html(botmcpy);
                   //document.getElementById(botm_cpy).innerHTML(botmcpy);
               </script>
               <script language="javascript" src="//www.ccgp.gov.cn/images/vr.js"></script>
               </div>
           </div>
           </body>
           <script language="javascript" src="/js/detailaddon.js"></script>
       </html>
       """
    return extract_content(html_content)

if __name__ == '__main__':
   print(extract_content_test())


data = \
{
"项目编号": "",
"项目名称": "",
"采购单位": "",
"中标供应商": {
"名称": "",
"地址": "",
"中标金额": "",
"评审得分": ""
},
"公告时间": ""
}

