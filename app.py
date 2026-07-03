import streamlit as st
import pandas as pd
import io

# ضبط الشاشة لتكون مريحة تماماً للموبايل
st.set_page_config(page_title="لوحة التسكين السريعة", layout="wide")

# تنسيق الواجهة لتدعم اللغة العربية وتبسيط أزرار التحكم
st.markdown("""
    <style>
    body, div, input, textarea, p, span, h1, h2, h3 { text-align: right; direction: rtl; }
    
    /* تحسين شكل المربعات لتشبه لوحة تحكم حية سريعة */
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 12px;
        margin-top: 15px;
    }
    .room-box {
        background-color: #1e293b;
        border: 2px solid #475569;
        border-radius: 10px;
        padding: 12px;
    }
    .room-header-title {
        color: #38bdf8;
        font-weight: bold;
        font-size: 15px;
        border-bottom: 1px solid #334155;
        padding-bottom: 5px;
        margin-bottom: 8px;
    }
    .bed-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 5px;
        margin-bottom: 8px;
    }
    .bed-unit {
        aspect-ratio: 1;
        border-radius: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
    }
    .bed-full { background-color: #0369a1; border: 1px solid #38bdf8; }
    .bed-empty { background-color: #0f172a; border: 1px dashed #475569; }
    
    .guest-line {
        background-color: rgba(15, 23, 42, 0.5);
        color: #cbd5e1;
        padding: 2px 6px;
        margin-bottom: 3px;
        border-radius: 4px;
        font-size: 12px;
        display: block;
        text-overflow: ellipsis;
        white-space: nowrap;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ نظام تسكين الفندق وإصدار Excel السريع")

# 1. تهيئة الذاكرة للغرف
if "custom_rooms" not in st.session_state:
    # نترك قائمة افتراضية مكتوبة ليسهل على المستخدم رؤية الطريقة ومسحها فوراً
    st.session_state.custom_rooms = [
        {"id": "غرفة 1", "capacity": 8},
        {"id": "غرفة 2", "capacity": 7},
        {"id": "غرفة 3", "capacity": 5}
    ]

# تقسيم الواجهة لسهولة الحركة من الموبايل
col_inputs, col_screen = st.columns([1.2, 2.5])

with col_inputs:
    st.subheader("📝 الخطوة 1: إدارة وتعديل الغرف وسرايرها")
    
    # تحويل القائمة الحالية لنص ليسهل تعديله وحذفه فوراً
    rooms_text_init = ""
    for r in st.session_state.custom_rooms:
        rooms_text_init += f"{r['id']}: {r['capacity']}\n"
        
    rooms_input = st.text_area(
        "اكتب الغرف المتاحة هنا (يمكنك التعديل، المسح، أو الإضافة مباشرة):",
        value=rooms_text_init,
        height=180,
        help="اكتب اسم الغرفة ثم نقطتين ثم عدد السراير. مثال: غرفة 10: 4",
        placeholder="غرفة 1: 5\nغرفة 2: 4\nغرفة 3: 5"
    )
    
    # تحديث الغرف تلقائياً من المربع النصي بدون أزرار معقدة
    new_rooms_list = []
    if rooms_input:
        lines = rooms_input.strip().split("\n")
        for line in lines:
            if ":" in line:
                parts = line.split(":")
                r_name = parts[0].strip()
                try:
                    r_cap = int(parts[1].strip())
                    if r_name and r_cap > 0:
                        new_rooms_list.append({"id": r_name, "capacity": r_cap})
                except:
                    pass
        st.session_state.custom_rooms = new_rooms_list

    st.write("---")
    st.subheader("👥 الخطوة 2: إدخال النزلاء")
    
    guests_raw = st.text_area(
        "الصق أو اكتب أسماء النزلاء هنا (اسم في كل سطر):",
        height=180,
        placeholder="انسخ القائمة من الواتساب والصقها هنا مباشرة..."
    )
    
    # تنظيف الأسماء المكتوبة
    guests_list = [g.strip() for g in guests_raw.replace(",", "\n").split("\n") if g.strip()]
    
    # حساب السعة لايف
    total_beds_count = sum(r["capacity"] for r in st.session_state.custom_rooms)
    st.info(f"📊 السراير المتاحة بالفندق: {total_beds_count} | النزلاء المطلوبين: {len(guests_list)}")

    # خوارزمية التسكين السريع
    room_assignments = {}
    if st.session_state.custom_rooms:
        # ترتيب الغرف من الأكبر سعة للأصغر لتوفير أعلى كفاءة
        sorted_hotel_rooms = sorted(st.session_state.custom_rooms, key=lambda x: x["capacity"], reverse=True)
        room_assignments = {r["id"]: {"capacity": r["capacity"], "guests": []} for r in sorted_hotel_rooms}
        
        g_idx = 0
        for rm in sorted_hotel_rooms:
            rid = rm["id"]
            rcap = rm["capacity"]
            while len(room_assignments[rid]["guests"]) < rcap and g_idx < len(guests_list):
                room_assignments[rid]["guests"].append(guests_list[g_idx])
                g_idx += 1
                
        # عرض الأشخاص الزائدين عن السعة
        if g_idx < len(guests_list):
            st.error(f"🚨 متبقي {len(guests_list) - g_idx} فرد لم يجدوا سراير!")
            st.caption(", ".join(guests_list[g_idx:]))

    # زر إصدار الإكسيل
    if len(guests_list) > 0 and room_assignments:
        export_data = []
        for rm in st.session_state.custom_rooms:
            rid = rm["id"]
            data = room_assignments.get(rid, {"guests": []})
            export_data.append({
                "اسم الغرفة": rid,
                "عدد السراير": rm["capacity"],
                "المسكنين فعلياً": len(data["guests"]),
                "الأسماء داخل الغرفة": ", ".join(data["guests"]) if data["guests"] else "فارغة"
            })
            
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            pd.DataFrame(export_data).to_excel(writer, index=False)
        excel_buffer.seek(0)
        
        st.download_button(
            label="📥 اضغط هنا لحفظ ملف Excel فورا",
            data=excel_buffer,
            file_name="كشف_التسكين_السريع.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

with col_display:
    st.subheader("🎬 لوحة التسكين التفاعلية لايف")
    
    if not st.session_state.custom_rooms:
        st.warning("يرجى كتابة الغرف في المربع الأيمن أولاً ليبدأ النظام بالعمل.")
    else:
        # بناء لوحة التحكم المباشرة
        dashboard_html = '<div class="dashboard-grid">'
        
        for room in st.session_state.custom_rooms:
            rid = room["id"]
            data = room_assignments.get(rid, {"guests": []})
            g_in_room = data["guests"]
            
            # رص السراير بصرياً
            beds_view = '<div class="bed-container">'
            for b in range(room["capacity"]):
                if b < len(g_in_room):
                    beds_view += f'<div class="bed-unit bed-full" title="{g_in_room[b]}">🛏️</div>'
                else:
                    beds_view += '<div class="bed-unit bed-empty"></div>'
            beds_view += '</div>'
            
            # رص الأسماء
            names_view = ''
            if g_in_room:
                for guest_name in g_in_room:
                    names_view += f'<span class="guest-line">👤 {guest_name}</span>'
            else:
                names_view += '<span style="color:#64748b; font-size:12px; display:block; text-align:center;">فارغة</span>'
                
            dashboard_html += f"""
                <div class="room-box">
                    <div class="room-header-title">{rid} <span style="font-size:12px; color:#94a3b8; float:left;">{len(g_in_room)}/{room["capacity"]}</span></div>
                    {beds_view}
                    {names_view}
                </div>
            """
            
        dashboard_html += '</div>'
        st.markdown(dashboard_html, unsafe_allow_html=True)
