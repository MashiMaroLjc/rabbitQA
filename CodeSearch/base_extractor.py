class Extractor:
    def __init__(self):
        pass

    def _clean(self, text):
        """
        清理掉一些特殊符号
        :return:
        """
        symbol = [">>>", "\r", "\t", "\xa0", "\u3000"]
        for sym in symbol:
            text = text.replace(sym,"")
        return text

    def extract_code(self, soup):
        """

        :param soup:
        :return:
        """
        result = []
        p_list = soup.find_all("p")
        for p in p_list:
            text = self._clean(p.get_text())
            result.extend(text.split("\n"))
        code_list = soup.find_all("code")
        for code in code_list:
            # c = code.get_text()
            text = self._clean(code.get_text())
            result.extend(text.split("\n"))
        return result
