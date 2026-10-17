import json
import requests

# رابط البيانات الخاصة بك (تأكد من تعديل API إذا كنت تستخدم مصدراً معيناً)
# هذا الكود يضمن جلب بيانات اللاعبين مع الأهداف والأسيست والبطاقات

def fetch_and_save_data():
    print("جلب بيانات اللاعبين والإحصائيات...")
    
    # مثال لتحديث قائمة اللاعبين مع إحصائياتهم
    # انقل الهيكل الموجود لديك وضيف عليه هذه الحقول:
    players_data = []
    
    # ... كود جلب البيانات الخاص بك ...
    
    # تأكد أن كل عنصر لاعب يحتوي على الحقول التالية:
    # player_entry = {
    #     "id": player_id,
    #     "name": player_name,
    #     "goals": goals_count,       # ⚽ الأهداف
    #     "assists": assists_count,   # 🎯 الأسيست
    #     "yellow_cards": yellow_c,   # 🟨 البطاقات الصفراء
    #     "red_cards": red_c          # 🟥 البطاقات الحمراء
    # }
    
    # حفظ البيانات في ملف players.json
    with open('data/players.json', 'w', encoding='utf-8') as f:
        json.dump(players_data, f, ensure_ascii=False, indent=4)
        
    print("تم الحفظ بنجاح مع بيانات الأهداف والإحصائيات! ✅")

if __name__ == "__main__":
    fetch_and_save_data()
