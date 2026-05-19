import random
import datetime
from . import config, db

def get_country_power(country):
    prof = config.COUNTRY_PROFILES.get(country, {"gdp":0.5, "military":0, "alliances":[]})
    base = prof["gdp"]*0.4 + prof["military"]*1.2
    alliance_bonus = len(prof["alliances"]) * 2
    return base + alliance_bonus

def generate_random_event():
    events = [
        {"name": "Doğal Afet", "effect": {"Ekonomi": -15, "Prestij": -5}},
        {"name": "Lider Değişimi", "effect": {"Prestij": -10, "Güvenlik": -5}},
        {"name": "Skandal", "effect": {"Prestij": -20}},
        {"name": "Ekonomik Kriz", "effect": {"Ekonomi": -20}},
        {"name": "Teknolojik Atılım", "effect": {"Ekonomi": 10, "Prestij": 5}}
    ]
    return random.choice(events)

class SimulatorSession:
    def __init__(self, country1, country2, issue, strategy):
        self.country1 = country1
        self.country2 = country2
        self.issue = issue
        self.strategy = strategy
        self.step = 1
        self.total_steps = 3  # 3-5 arası yapılabilir
        self.metrics = {m: 0 for m in config.METRICS}
        self.log = []
        self.finished = False

    def get_options(self):
        """Her adımda kullanıcıya gösterilecek kararlar."""
        if self.issue == "Ticaret":
            return ["Gümrük indirimi teklif et", "Yaptırım tehdidi", "Karşılıklı yatırım"]
        elif self.issue == "Güvenlik":
            return ["Askerî iş birliği öner", "Sınır güvenliği protokolü", "Silah kontrolü"]
        elif self.issue == "İklim":
            return ["Emisyon hedefi belirle", "Yeşil fon oluştur", "Teknoloji transferi"]
        elif self.issue == "Enerji":
            return ["Boru hattı anlaşması", "Nükleer iş birliği", "Fiyat sabitleme"]
        else:  # Göç
            return ["Kota artırımı", "Geri kabul anlaşması", "Entegrasyon programı"]

    def apply_decision(self, decision):
        """
        Karara göre metrikleri güncelle, ülke profillerinden etkilen.
        Rastgele bir olay tetiklenebilir.
        """
        # Baz etkiler
        base_effects = {
            "Ekonomi": random.randint(-5, 10),
            "Güvenlik": random.randint(-5, 10),
            "Prestij": random.randint(-5, 10)
        }

        # Kararın stratejiyle uyumu
        if self.strategy == "İşbirlikçi" and "iş birliği" in decision.lower():
            base_effects["Ekonomi"] += 5
            base_effects["Prestij"] += 3
        elif self.strategy == "Rekabetçi" and ("tehdit" in decision.lower() or "yaptırım" in decision.lower()):
            base_effects["Güvenlik"] += 4
            base_effects["Ekonomi"] -= 2
        else:
            base_effects["Prestij"] += 2

        # Ülke profillerine göre bonus
        power1 = get_country_power(self.country1)
        power2 = get_country_power(self.country2)
        if power1 > power2:
            base_effects["Prestij"] += 2
        elif power2 > power1:
            base_effects["Prestij"] -= 2

        # Rastgele olay
        event = None
        if random.random() < 0.4:  # %40 ihtimalle kriz
            event = generate_random_event()
            for k, v in event["effect"].items():
                base_effects[k] = base_effects.get(k, 0) + v

        # Metriklere yansıt
        for k in config.METRICS:
            self.metrics[k] += base_effects.get(k, 0)

        # Log
        log_entry = {"step": self.step, "decision": decision, "effects": base_effects.copy(), "event": event}
        self.log.append(log_entry)
        self.step += 1
        if self.step > self.total_steps:
            self.finished = True

    def get_final_result(self):
        """Simülasyon bittiğinde döndürülecek özet."""
        total_score = sum(self.metrics.values())
        # Sonuç cümlesi
        if total_score > 15:
            result = "Anlaşma büyük ölçüde başarılı."
        elif total_score > 0:
            result = "Kısmi anlaşma sağlandı."
        else:
            result = "Müzakereler başarısız oldu."

        analysis = {
            "İşbirlikçi": "Uzun vadeli iş birliği temelleri atıldı.",
            "Rekabetçi": "Kısa vadeli kazanç elde edildi ancak güven sarsıldı.",
            "Karma": "Dengeli sonuç, her iki tarafı da memnun etti."
        }[self.strategy]

        # Teori eşleştirme
        if self.issue in ["Güvenlik", "Enerji"]:
            theory = "Realizm"
        elif self.issue in ["Ticaret", "Göç"]:
            theory = "Liberalizm"
        else:
            theory = "Konstrüktivizm"

        resource = random.choice(config.RESOURCES)

        return {
            "country1": self.country1,
            "country2": self.country2,
            "issue": self.issue,
            "strategy": self.strategy,
            "metrics": self.metrics,
            "total_score": total_score,
            "result": result,
            "analysis": analysis,
            "theory": theory,
            "theory_desc": config.THEORY_CARDS[theory],
            "resource": resource,
            "log": self.log,
            "timestamp": datetime.datetime.now().isoformat()
        }
