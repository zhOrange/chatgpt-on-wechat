from bot.bot_factory import create_bot
from bridge.context import Context
from bridge.reply import Reply
from common import const
from common.log import logger
from common.singleton import singleton
from config import conf
from translate.factory import create_translator
from voice.factory import create_voice


@singleton
class Bridge(object):
    def __init__(self):
        self.btype = {
            "chat": const.CHATGPT,
            "voice_to_text": conf().get("voice_to_text", "openai"),
            "text_to_voice": conf().get("text_to_voice", "google"),
            "translate": conf().get("translate", "baidu"),
        }
        model_type = conf().get("model") or const.GPT35
        if model_type in ["text-davinci-003"]:
            self.btype["chat"] = const.OPEN_AI
        if conf().get("use_azure_chatgpt", False):
            self.btype["chat"] = const.CHATGPTONAZURE
        if model_type in ["wenxin", "wenxin-4"]:
            self.btype["chat"] = const.BAIDU
        if model_type in ["xunfei"]:
            self.btype["chat"] = const.XUNFEI
        if model_type in [const.QWEN]:
            self.btype["chat"] = const.QWEN
        if model_type in [const.GEMINI]:
            self.btype["chat"] = const.GEMINI
        if model_type in [const.ZHIPU_AI]:
            self.btype["chat"] = const.ZHIPU_AI
        if model_type in [const.GROQ_LLAMA2, const.GROQ_MIXTRAL]:
            self.btype["chat"] = const.GROQ
        self.btype["voice_to_text"] = conf().get("voice_to_text", "openai")
        self.btype["text_to_voice"] = conf().get("text_to_voice", "google")

        if conf().get("use_linkai") and conf().get("linkai_api_key"):
            self.btype["chat"] = const.LINKAI
            if not conf().get("voice_to_text") or conf().get("voice_to_text") in ["openai"]:
                self.btype["voice_to_text"] = const.LINKAI
            if not conf().get("text_to_voice") or conf().get("text_to_voice") in ["openai", const.TTS_1, const.TTS_1_HD]:
                self.btype["text_to_voice"] = const.LINKAI

        if model_type in ["claude"]:
            self.btype["chat"] = const.CLAUDEAI
        self.bots = {}
        self.chat_bots = {}

    def get_bot(self, typename):
        if self.bots.get(typename) is None:
            logger.info("create bot {} for {}".format(self.btype[typename], typename))
            if typename == "text_to_voice":
                self.bots[typename] = create_voice(self.btype[typename])
            elif typename == "voice_to_text":
                self.bots[typename] = create_voice(self.btype[typename])
            elif typename == "chat":
                self.bots[typename] = create_bot(self.btype[typename])
            elif typename == "translate":
                self.bots[typename] = create_translator(self.btype[typename])
        return self.bots[typename]

    def get_bot_type(self, typename):
        return self.btype[typename]

    def fetch_reply_content(self, query, context: Context) -> Reply:
        return self.get_bot("chat").reply(query, context)

    def fetch_voice_to_text(self, voiceFile) -> Reply:
        bot_v2t = self.get_bot("voice_to_text")
        return bot_v2t.voiceToText(voiceFile)

    def fetch_text_to_voice(self, text) -> Reply:
        bot_t2v = self.get_bot("text_to_voice")
        return bot_t2v.textToVoice(text)

    def fetch_translate(self, text, from_lang="", to_lang="en") -> Reply:
        return self.get_bot("translate").translate(text, from_lang, to_lang)

    def find_chat_bot(self, bot_type: str):
        if self.chat_bots.get(bot_type) is None:
            self.chat_bots[bot_type] = create_bot(bot_type)
        return self.chat_bots.get(bot_type)

    def reset_bot(self):
        """
        重置bot路由
        """
        self.__init__()
