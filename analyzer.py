import matplotlib.pyplot as plt
import io

def nedelnyy_otchet(zapisi):
    if not zapisi:
        return "Нет данных за 7 дней."
    n = len(zapisi)
    sred_nastroenie = sum(z['nastroenie'] for z in zapisi) / n
    sred_ucheba = sum(z['chasy_ucheby'] for z in zapisi) / n
    sred_son = sum(z['chasy_sna'] for z in zapisi) / n
    return f"📊 За неделю:\n😊 {sred_nastroenie:.1f}/5\n📚 {sred_ucheba:.1f} ч\n😴 {sred_son:.1f} ч"

def mesyachnyy_otchet(zapisi):
    if not zapisi:
        return "Нет данных за 30 дней."
    n = len(zapisi)
    sred_nastroenie = sum(z['nastroenie'] for z in zapisi) / n
    sred_ucheba = sum(z['chasy_ucheby'] for z in zapisi) / n
    sred_son = sum(z['chasy_sna'] for z in zapisi) / n
    return f"📅 За месяц:\n😊 {sred_nastroenie:.1f}/5\n📚 {sred_ucheba:.1f} ч\n😴 {sred_son:.1f} ч"

def generirovat_insayty(zapisi):
    if len(zapisi) < 5:
        return "Мало данных (нужно минимум 5 дней)."
    malo_sna = [z for z in zapisi if z['chasy_sna'] < 7]
    mnogo_sna = [z for z in zapisi if z['chasy_sna'] >= 7]
    malo_ucheby = [z for z in zapisi if z['chasy_ucheby'] < 3]
    mnogo_ucheby = [z for z in zapisi if z['chasy_ucheby'] >= 3]
    tekst = "🧠 Инсайты:\n"
    if malo_sna and mnogo_sna:
        sr_malo = sum(z['nastroenie'] for z in malo_sna) / len(malo_sna)
        sr_mnogo = sum(z['nastroenie'] for z in mnogo_sna) / len(mnogo_sna)
        tekst += f"• Сон <7 ч → настроение {sr_malo:.1f}, ≥7 ч → {sr_mnogo:.1f}\n"
    if malo_ucheby and mnogo_ucheby:
        sr_malo = sum(z['nastroenie'] for z in malo_ucheby) / len(malo_ucheby)
        sr_mnogo = sum(z['nastroenie'] for z in mnogo_ucheby) / len(mnogo_ucheby)
        tekst += f"• Учёба <3 ч → настроение {sr_malo:.1f}, ≥3 ч → {sr_mnogo:.1f}\n"
    return tekst

def postroit_grafik_nastroeniya(zapisi):
    if not zapisi:
        return None
    daty = [z['data'].strftime("%Y-%m-%d") for z in zapisi]
    nastroeniya = [z['nastroenie'] for z in zapisi]
    plt.figure(figsize=(10, 5))
    plt.plot(daty, nastroeniya, marker='o')
    plt.title("Динамика настроения")
    plt.xlabel("Дата")
    plt.ylabel("Настроение (1-5)")
    plt.ylim(0.5, 5.5)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf