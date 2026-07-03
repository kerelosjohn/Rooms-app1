import streamlit as st
import pandas as pd
import io

# إعدادات الشاشة لتناسب الموبايل والكمبيوتر
st.set_page_config(page_title="لوحة التسكين التفاعلية", layout="wide")

# تنسيق الواجهة لتبدو كشاشة عرض سينمائية ذكية (RTL)
st.markdown("""
    <style>
    body, div, input, textarea, p, span, h1, h3 { text-align: right; direction: rtl; }
    .stTabs [data-baseweb="tab-list"] { direction: rtl; }
    
    /* تصميم كروت الغرف التفاعلية */
    .room-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 16px;
        margin-top: 15px;
    }
    .room-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .room-title {
        color: #38bdf8;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 8px;
        border-bottom: 1px solid #334155;
        padding-bottom: 4px;
    }
    /* تصميم السراير */
    .beds-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 6px;
        margin-bottom: 12px;
    }
    .bed-icon {
        aspect-ratio: 1;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
    }
    .bed-occupied { background-color: #0369a1; border: 1px solid #38bdf8; }
    .bed-empty { background-color: #0f172a; border: 1px dashed #475569; }
    
    /* قائمة النزلاء داخل الكارت */
    .guest-tag {
        background-color: rgba(15, 23, 42, 0.6);
        color: #e2e8f0;
        padding: 4px 8px;
        margin-bottom: 4px;
        border-radius: 4px;
        font-size: 13px;
        display: block;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 لوحة إدارة وتسكين الغرف الفندقية")

# تهيئة مخزن الغرف ليكون فارغاً تماماً من البداية بناءً على طلبك الجديد
if "rooms_list" not in st.session_state:
    st.session_state.rooms_list = []

# تقسيم الشاشة إلى لوحة جانبية ولوحة العرض الرئيسية
col_panel, col_display = st.columns([1, 2.5])

with col_panel:
    st.subheader("🛠️ الإعداد والتحكم")
    
    # نموذج إضافة غرفة جديدة (مفتوح وجاهز للاستخدام)
    st.write("### ➕ إضافة غرفة للفندق")
    new_name = st.text_input("اسم أو رقم الغرفة:")
    new_beds = st.number_input("عدد سراير الغرفة:", min_value=1, max_value=50, value=5)
    if st.button("حفظ وإضافة الغرفة"):
        if new_name:
            if any(r["id"] == new_name for r in st.session_state.rooms_list):
                st.error("⚠️ اسم هذه الغرفة مسجل بالفعل!")
            else:
                st.session_state.rooms_list.append({"id": new_name, "capacity": new_beds})
                st.success(f"تم إضافة {new_name} بنجاح!")
                st.rerun()
        else:
            st.error("برجاء كتابة اسم أو رقم الغرفة أولاً.")

    st.write("---")

    # حساب السراير المتاحة حالياً بناءً على ما أدخلته أنت
    rooms_df = pd.DataFrame(st.session_state.rooms_list)
    total_beds = int(rooms_df["capacity"].sum()) if not rooms_df.empty else 0
    st.info(f"📊 إجمالي الطاقة الحالية: **{total_beds} سريراً متاحاً**")
    
    # مربع إدخال النزلاء
    guests_input = st.text_area("أدخل أسماء النزلاء (اسم في كل سطر):", height=200, placeholder="محمد أحمد\nكريم علي\nسارة محمود...")
    
    # تنظيف ومعالجة الأسماء المدخلة
    guests = [g.strip() for g in guests_input.replace(",", "\n").split("\n") if g.strip()]
    
    # خوارزمية التسكين الفوري (ترتيب الغرف تنازلياً لملء الأكبر أولاً)
    assignments = {}
    if not rooms_df.empty:
        sorted_rooms = sorted(st.session_state.rooms_list, key=lambda x: x["capacity"], reverse=True)
        assignments = {r["id"]: {"capacity": r["capacity"], "guests": []} for r in sorted_rooms}
        
        guest_index = 0
        for room in sorted_rooms:
            r_id = room["id"]
            cap = room["capacity"]
            while len(assignments[r_id]["guests"]) < cap and guest_index < len(guests):
                assignments[r_id]["guests"].append(guests[guest_index])
                guest_index += 1
                
        # عرض تنبيه إذا كانت السعة لا تكفي
        if guest_index < len(guests):
            leftover = len(guests) - guest_index
            st.error(f"🚨 قائمة الانتظار: متبقي {leftover} فرد بدون سراير!")
            with st.expander("استعراض أسماء المتبقين"):
                st.write(", ".join(guests[guest_index:]))

    # زر تصدير الإكسيل المنسق والمحمي للغة العربية
    if len(guests) > 0 and assignments:
        report_rows = []
        for room in st.session_state.rooms_list:
            r_id = room["id"]
            data = assignments.get(r_id, {"guests": []})
            status = "مكتملة" if len(data["guests"]) == room["capacity"] else ("فارغة" if len(data["guests"]) == 0 else "متاح بها أماكن")
            report_rows.append({
                "رقم / اسم الغرفة": r_id,
                "سعة السراير الكلية": room["capacity"],
                "عدد المسكنين فعلياً": len(data["guests"]),
                "حالة الغرفة": status,
                "أسماء المقيمين": ", ".join(data["guests"]) if data["guests"] else "لا يوجد"
            })
        
        excel_df = pd.DataFrame(report_rows)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            excel_df.to_excel(writer, index=False, sheet_name="كشف التسكين")
        buffer.seek(0)
        
        st.download_button(
            label="📥 تحميل الكشف النهائي (Excel)",
            data=buffer,
            file_name="كشف_تسكين_الغرف_السينمائي.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

with col_display:
    st.subheader("🎬 شاشة العرض السينمائي لحالة الغرف والنزلاء لايف")
    
    if not st.session_state.rooms_list:
        st.warning("الفندق فارغ حالياً. يرجى البدء بإضافة غرف جديدة من اللوحة الجانبية اليمين.")
    else:
        # فتح الحاوية الكبيرة لكروت الغرف
        html_content = '<div class="room-container">'
        
        # المرور على الغرف وبناء التصميم بداخلها
        for index, room in enumerate(st.session_state.rooms_list):
            r_id = room["id"]
            # جلب النزلاء المسكنين في هذه الغرفة (إن وجدوا)
            room_data = assignments.get(r_id, {"guests": []})
            room_guests = room_data["guests"]
            
            # بناء كتل السراير (الأزرق محجوز، الداكن فارغ)
            beds_html = '<div class="beds-grid">'
            for b_idx in range(room["capacity"]):
                if b_idx < len(room_guests):
                    beds_html += f'<div class="bed-icon bed-occupied" title="{room_guests[b_idx]}">🛏️</div>'
                else:
                    beds_html += '<div class="bed-icon bed-empty"></div>'
            beds_html += '</div>'
            
            # بناء أسماء النزلاء أسفل السراير الكارد
            guests_html = ''
            if room_guests:
                for guest in room_guests:
                    guests_html += f'<span class="guest-tag">👤 {guest}</span>'
            else:
                guests_html += '<span style="color:#64748b; font-size:12px; display:block; text-align:center;">غرفة فارغة</span>'
            
            # تجميع الكارد الكامل للغرفة الحالية
            html_content += f"""
                <div class="room-card">
                    <div class="room-title">{r_id} <span style="font-size:12px; color:#94a3b8; float:left;">{len(room_guests)}/{room["capacity"]}</span></div>
                    {beds_html}
                    {guests_html}
                </div>
            """
            
        html_content += '</div>'
        st.markdown(html_content, unsafe_allow_html=True)
        
        # لوحة سريعة لحذف أو تعديل مسميات وسراير الغرف بالأسفل
        st.write("---")
        with st.expander("⚙️ لوحة حذف وتعديل الغرف الحالية والسراير"):
            mod_col1, mod_col2 = st.columns(2)
            with mod_col1:
                room_to_del = st.selectbox("اختر غرفة لحذفها نهائياً:", ["-- اختر غرفة --"] + [r["id"] for r in st.session_state.rooms_list])
                if room_to_del != "-- اختر غرفة --" and st.button("تأكيد حذف الغرفة"):
                    st.session_state.rooms_list = [r for r in st.session_state.rooms_list if r["id"] != room_to_del]
                    st.success(f"تم حذف {room_to_del}")
                    st.rerun()
            with mod_col2:
                room_to_rename = st.selectbox("اختر غرفة لتعديل بياناتها:", ["-- اختر غرفة --"] + [r["id"] for r in st.session_state.rooms_list])
                new_room_title = st.text_input("الاسم الجديد للغرفة (اختياري):")
                edit_beds_count = st.number_input("تحديث عدد السراير لهذه الغرفة:", min_value=1, max_value=50, value=5)
                
                if room_to_rename != "-- اختر غرفة --" and st.button("تحديث البيانات"):
                    for r in st.session_state.rooms_list:
                        if r["id"] == room_to_rename:
                            if new_room_title:
                                r["id"] = new_room_title
                            r["capacity"] = edit_beds_count
                    st.success("تم التحديث بنجاح")
                    st.rerun()
