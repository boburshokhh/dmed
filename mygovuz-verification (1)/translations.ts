export type Language = 'ru' | 'en' | 'uz';

export const translations = {
  ru: {
    header: {
      home: "Главная",
      login: "Войти",
      language: "Язык",
      langCode: "RU"
    },
    alert: {
      text: "Пожалуйста пройдите авторизацию чтобы система определила вас. Если документ принадлежит вам, введения ПИН кода не требуется. ",
      link: "Нажмите здесь для авторизации"
    },
    form: {
      title: "Введите PIN-код для просмотра документа",
      label: "ПИН код",
      button: "Открыть",
      helper: "PIN-код размещается рядом с QR-кодом документа"
    }
  },
  en: {
    header: {
      home: "Home",
      login: "Login",
      language: "Language",
      langCode: "EN"
    },
    alert: {
      text: "Please log in so the system can identify you. If the document belongs to you, entering the PIN code is not required. ",
      link: "Click here to log in"
    },
    form: {
      title: "Enter PIN code to view document",
      label: "PIN code",
      button: "Open",
      helper: "The PIN code is located next to the document's QR code"
    }
  },
  uz: {
    header: {
      home: "Bosh sahifa",
      login: "Kirish",
      language: "Til",
      langCode: "UZ"
    },
    alert: {
      text: "Iltimos, tizim sizni aniqlashi uchun autentifikatsiyadan o'ting. Agar hujjat sizga tegishli bo'lsa, PIN kodini kiritish talab qilinmaydi. ",
      link: "Autentifikatsiyadan o'tish uchun bu yerni bosing"
    },
    form: {
      title: "Hujjatni ko'rish uchun PIN kodini kiriting",
      label: "PIN kod",
      button: "Ochish",
      helper: "PIN kodi hujjatning QR kodi yonida joylashgan"
    }
  }
};