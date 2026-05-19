import random
import datetime
from . import config

def run_multi_step_simulation(country1, country2, issue, strategy):
    steps = [
        f"Taraflar {issue} konusunda ön görüşmeleri başlattı.",
        f"{strategy} stratejisi çerçevesinde pozisyonlar netleşti.",
        f"Son tur müzakerelerde anlaşma metni hazırlandı."
    ]
    # Rastgele metrik değişimleri (-10 ile +20 arası)
    metrics = {m: random.randint(-10, 20) for m in config.METRICS}
    # Sonuç cümleleri
    outcomes = {
        "Ticaret": ["Gümrük tarifelerinde %10 indirim.", "Serbest ticaret anlaşması.", "Müzakereler çıkmaza girdi."],
        "Güvenlik": ["Askerî iş birliği protokolü.", "Ortak devriye kararı.", "Silah satışı anlaşmazlığı."],
        "İklim": ["Karbon emisyonu hedefleri ortak.", "Yeşil enerji fonu.", "Anlaşma ertelendi."],
        "Enerji": ["Doğal gaz boru hattı anlaşması.", "Nükleer iş birliği.", "Enerji fiyatları uzlaşmazlığı."],
        "Göç": ["Mülteci kotaları anlaşması.", "Geri kabul anlaşması.", "Görüşmeler sonuçsuz."]
    }
    result_text = random.choice(outcomes[issue])
    # Stratejiye göre analiz
    analysis = {
        "İşbirlikçi": "Karşılıklı kazanç sağlandı, uzun vadeli ilişkiler güçlendi.",
        "Rekabetçi": "Kısa vadede kazanç elde edildi ama güven zedelendi.",
        "Karma": "Dengeli yaklaşım her iki tarafı kısmen tatmin etti."
    }[strategy]

    # Teori kartı eşleştirme
    if issue in ["Güvenlik", "Enerji"]:
        theory = "Realizm"
    elif issue in ["Ticaret", "Göç"]:
        theory = "Liberalizm"
    else:
        theory = "Konstrüktivizm"

    resource = random.choice(config.RESOURCES)

    return {
        "country1": country1,
        "country2": country2,
        "issue": issue,
        "strategy": strategy,
        "steps": steps,
        "metrics": metrics,
        "total_score": sum(metrics.values()),
        "result": result_text,
        "analysis": analysis,
        "theory": theory,
        "theory_desc": config.THEORY_CARDS[theory],
        "resource": resource,
        "timestamp": datetime.datetime.now().isoformat()
    }
