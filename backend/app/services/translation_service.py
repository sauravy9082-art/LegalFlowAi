from typing import Dict

class MultilingualExplanationService:
    DICTIONARY = {
        "security deposit forfeiture": {
            "en": "This clause allows forfeiture of your deposit if terms are broken.",
            "hi": "यह खंड सुरक्षा जमा जब्त करने की अनुमति देता है यदि शर्तें तोड़ी जाती हैं।",
            "mr": "हा नियम अटींचे उल्लंघन झाल्यास तुमची सुरक्षा ठेव जप्त करण्याची परवानगी देतो.",
            "ta": "விதிமுறைகள் மீறப்பட்டால் உங்கள் வைப்புத் தொகையை இழக்க இந்த பிரிவு அனுமதிக்கிறது.",
            "es": "Esta cláusula permite la confiscación de su depósito si se incumplen los términos.",
            "fr": "Cette clause permet la confiscation de votre dépôt en cas de non-respect des conditions."
        },
        "unilateral discretion": {
            "en": "The other party reserves sole power to modify rules without your prior consent.",
            "hi": "दूसरी पार्टी के पास आपकी पूर्व सहमति के बिना नियमों को बदलने का एकमात्र अधिकार है।",
            "mr": "दुसऱ्या पक्षाकडे तुमच्या पूर्वसंमतीशिवाय नियम बदलण्याचे एकमेव अधिकार आहेत.",
            "ta": "உங்கள் முன் அனுமதியின்றி விதிகளை மாற்ற மற்ற தரப்பிற்கு மட்டுமே அதிகாரம் உள்ளது.",
            "es": "La otra parte se reserva el poder exclusivo de modificar las reglas sin su consentimiento previo.",
            "fr": "L'autre partie se réserve le pouvoir exclusif de modifier les règles sans votre consentement préalable."
        },
        "uncapped liability": {
            "en": "You face unlimited financial liability for loss or damages.",
            "hi": "नुकसान के लिए आप पर असीमित वित्तीय देनदारी है।",
            "mr": "नुकसानीसाठी तुमच्यावर अमर्याद आर्थिक जबाबदारी आहे.",
            "ta": "சேதங்களுக்கு நீங்கள் எல்லையற்ற நிதிப் பொறுப்பை எதிர்நோக்குகிறீர்கள்.",
            "es": "Se enfrenta a una responsabilidad financiera ilimitada por pérdidas o daños.",
            "fr": "Vous faites face à une responsabilité financière illimitée pour les pertes ou dommages."
        }
    }

    @classmethod
    def get_translations(cls, text: str) -> Dict[str, str]:
        """
        Provides parallel translations for risk clause explanations.
        Standard fallbacks guarantee offline functionality without external internet API keys.
        """
        hi_text = "यह खंड आपकी जवाबदेही या समाप्ति की शर्तों को प्रभावित कर सकता है।"
        mr_text = "हा कलम तुमच्या जबाबदारी किंवा समाप्तीच्या अटींवर परिणाम करू शकतो."
        ta_text = "இந்த பிரிவு உங்கள் பொறுப்பு அல்லது முடிவுக் கதவுகளைப் பாதிக்கலாம்."
        es_text = "Esta cláusula puede afectar su responsabilidad o términos de rescisión."
        fr_text = "Cette clause peut affecter votre responsabilidad o vos conditions de résiliation."

        return {
            "en": text,
            "hi": hi_text,
            "mr": mr_text,
            "ta": ta_text,
            "es": es_text,
            "fr": fr_text
        }

    @classmethod
    def get_explanation(cls, category: str, text: str, language: str = "english") -> str:
        lang_lower = language.lower().strip()
        if lang_lower in ["hi", "hin", "hindi"]:
            code = "hi"
        elif lang_lower in ["mr", "mar", "marathi"]:
            code = "mr"
        elif lang_lower in ["ta", "tam", "tamil"]:
            code = "ta"
        elif lang_lower in ["es", "spa", "spanish"]:
            code = "es"
        elif lang_lower in ["fr", "fre", "french"]:
            code = "fr"
        else:
            code = "en"

        cat_key = category.lower().strip()
        for key, trans in cls.DICTIONARY.items():
            if key in cat_key or cat_key in key:
                return trans.get(code, trans["en"])

        translations = cls.get_translations(text)
        return translations.get(code, text)

# Alias for compatibility
TranslationService = MultilingualExplanationService
