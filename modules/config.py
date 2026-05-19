# Ülkeler ve bayrak emojileri
COUNTRIES = {
    "USA": "🇺🇸",
    "CHN": "🇨🇳",
    "RUS": "🇷🇺",
    "DEU": "🇩🇪",
    "FRA": "🇫🇷",
    "TUR": "🇹🇷",
    "IND": "🇮🇳",
    "BRA": "🇧🇷"
}

# Ülke kodlarına göre profil (statik, simülasyonu etkiler)
COUNTRY_PROFILES = {
    "USA": {"gdp": 25.0, "military": 10, "alliances": ["NATO", "AUKUS"]},
    "CHN": {"gdp": 18.0, "military": 9, "alliances": ["ŞİÖ"]},
    "RUS": {"gdp": 2.0, "military": 8, "alliances": ["BDT"]},
    "DEU": {"gdp": 4.5, "military": 5, "alliances": ["NATO", "AB"]},
    "FRA": {"gdp": 3.0, "military": 7, "alliances": ["NATO", "AB"]},
    "TUR": {"gdp": 1.0, "military": 6, "alliances": ["NATO"]},
    "IND": {"gdp": 3.5, "military": 8, "alliances": []},
    "BRA": {"gdp": 2.0, "military": 4, "alliances": ["BRICS"]}
}

ISSUES = ["Ticaret", "Güvenlik", "İklim", "Enerji", "Göç"]
STRATEGIES = ["İşbirlikçi", "Rekabetçi", "Karma"]

METRICS = ["Ekonomi", "Güvenlik", "Prestij"]

# IR Teori kartları
THEORY_CARDS = {
    "Realizm": "Devletler güç ve güvenlik peşindedir. Uluslararası sistem anarşiktir, iş birliği geçicidir.",
    "Liberalizm": "Kurumlar, ticaret ve demokrasi iş birliğini artırır. Karşılıklı bağımlılık barışı getirir.",
    "Konstrüktivizm": "Kimlikler ve normlar çıkarları şekillendirir. Müzakere süreci algıları değiştirebilir."
}

RESOURCES = [
    "📚 Joseph Nye – ‘Yumuşak Güç’",
    "📚 Hans Morgenthau – ‘Uluslararası Politika’",
    "📚 Robert Keohane – ‘After Hegemony’",
    "📚 Alexander Wendt – ‘Anarchy is What States Make of It’"
]

BADGES = {
    "first_sim": {"name": "İlk Adım", "desc": "İlk simülasyonunu tamamla"},
    "explorer": {"name": "Kâşif", "desc": "Tüm konuları dene"},
    "strategist": {"name": "Stratejist", "desc": "Tüm stratejileri kullan"},
    "pro_member": {"name": "Pro Üye", "desc": "Pro üyeliğe geç"},
    "credit_buyer": {"name": "Kredili", "desc": "Kredi paketi satın al"}
}

# Kullanıcı rolleri
ROLES = ["student", "teacher", "admin"]
