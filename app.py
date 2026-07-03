<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم والتسكين السينمائية</title>
    <!-- مكتبة الإكسيل -->
    <script src="https://jsdelivr.net"></script>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --primary: #38bdf8;
            --success: #10b981;
            --danger: #ef4444;
            --text: #f8fafc;
        }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background-color: var(--bg-color); 
            margin: 0; padding: 15px; color: var(--text); 
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { text-align: center; color: var(--primary); margin-bottom: 20px; font-size: 28px; text-shadow: 0 0 10px rgba(56, 189, 248, 0.4); }
        
        .main-grid { display: grid; grid-template-columns: 350px 1fr; gap: 20px; }
        @media (max-width: 992px) { .main-grid { grid-template-columns: 1fr; } }
        
        .panel { background: var(--card-bg); padding: 20px; border-radius: 12px; border: 1px solid #334155; height: fit-content; }
        h3 { margin-top: 0; color: var(--primary); border-bottom: 1px solid #334155; padding-bottom: 8px; }
        
        textarea { width: 100%; height: 180px; background: #0f172a; color: #fff; border: 1px solid #475569; border-radius: 8px; padding: 10px; font-size: 15px; box-sizing: border-box; }
        input, select { width: 100%; padding: 10px; background: #0f172a; color: #fff; border: 1px solid #475569; border-radius: 6px; box-sizing: border-box; margin-bottom: 12px; }
        
        button { width: 100%; padding: 12px; font-size: 15px; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; transition: 0.2s; margin-top: 5px; }
        .btn-blue { background-color: var(--primary); color: #000; }
        .btn-blue:hover { background-color: #7dd3fc; }
        .btn-green { background-color: var(--success); color: white; display: none; margin-top: 10px; }
        
        /* تصميم شاشة السينما ولوحة الغرف */
        .cinema-screen { 
            background: linear-gradient(180deg, rgba(56,189,248,0.2) 0%, rgba(0,0,0,0) 100%);
            border-top: 4px solid var(--primary); text-align: center; padding: 10px; margin-bottom: 25px;
            font-weight: bold; font-size: 14px; letter-spacing: 2px; color: var(--primary); box-shadow: 0 -10px 20px rgba(56,189,248,0.15);
        }
        
        .cinema-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 15px; }
        
        .room-card { 
            background: var(--card-bg); border: 1px solid #334155; border-radius: 10px; padding: 15px;
            display: flex; flex-direction: column; position: relative; transition: 0.3s;
        }
        .room-card:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        
        /* بار تعديل الرقم مباشرة */
        .room-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .editable-name { background: transparent; border: none; color: var(--primary); font-weight: bold; font-size: 16px; width: 110px; padding: 2px; margin: 0; }
        .editable-name:focus { background: #0f172a; border-bottom: 1px solid var(--primary); outline: none; }
        
        .beds-count { font-size: 12px; background: #475569; padding: 2px 6px; border-radius: 4px; }
        
        /* المقاعد أو السراير داخل الغرفة */
        .seats-container { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 5px; flex-grow: 1; }
        .seat { 
            aspect-ratio: 1; border-radius: 6px; background-color: #475569; 
            display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold;
            position: relative; cursor: pointer;
        }
        .seat.occupied { background-color: #0369a1; border: 1px solid var(--primary); }
        .seat.empty { background-color: #1e293b; border: 1px dashed #475569; }
        
        /* عرض الأسماء المنبثقة عند لمس السرير */
        .seat .tooltip {
            display: none; position: absolute; bottom: 125%; left: 50%; transform: translateX(-50%);
            background: #000; color: #fff; padding: 5px; border-radius: 4px; font-size: 11px;
            white-space: nowrap; z-index: 10; box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        .seat:hover .tooltip { display: block; }
        
        /* قائمة الأسماء داخل الغرفة لسهولة القراءة الكلية */
        .room-guests-list { margin-top: 10px; font-size: 13px; color: #cbd5e1; border-top: 1px solid #334155; padding-top: 5px; }
        .guest-item { background: rgba(0,0,0,0.2); padding: 3px 6px; margin-bottom: 3px; border-radius: 4px; display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        
        .action-zone { display: flex; justify-content: space-between; margin-top: auto; padding-top: 8px; }
        .btn-del-room { background: none; border: none; color: var(--danger); cursor: pointer; font-size: 12px; padding: 0; width: auto; margin: 0; }
        
        .stats-badge { background: #0369a1; padding: 8px; border-radius: 6px; text-align: center; margin-bottom: 15px; font-weight: bold; font-size: 14px; }
        .alert-box { background: rgba(239, 68, 68, 0.2); border: 1px solid var(--danger); color: #fca5a5; padding: 12px; border-radius: 8px; margin-bottom: 15px; font-size: 14px; }
    </style>
</head>
<body>

<div class="container">
    <h1>🏨 لوحة تسكين الغرف التفاعلية (شاشة العرض السينمائي)</h1>
    
    <div class="main-grid">
        <!-- لوحة التحكم الجانبية -->
        <div class="panel">
            <h3>🛠️ إعداد اللوحة والنزلاء</h3>
            <div class="stats-badge" id="totalBedsStats">إجمالي الطاقة: 88 سرير متاح</div>
            
            <label style="font-weight:bold; display:block; margin-bottom:5px;">1. أدخل أسماء النزلاء (اسم بالسطر):</label>
            <textarea id="guestsInput" placeholder="محمد أحمد&#10;كريم علي&#10;سارة محمود..."></textarea>
            
            <button class="btn-blue" style="margin-top:10px;" onclick="startAccommodation()">🚀 ابدأ التسكين الفوري</button>
            <button id="downloadBtn" class="btn-green" onclick="downloadExcel()">📥 تحميل الملف النهائي Excel</button>
            
            <h3 style="margin-top:25px; padding-top:10px;">➕ إضافة غرفة سريعة</h3>
            <input type="text" id="roomName" placeholder="رقم الغرفة (مثال: غرفة 18)">
            <input type="number" id="roomBeds" value="5" min="1" placeholder="عدد السراير">
            <button class="btn-blue" onclick="addRoom()">حفظ الغرفة الجديدة</button>
        </div>

        <!-- شاشة السينما التفاعلية للغرف -->
        <div>
            <div class="cinema-screen">🎬 شاشة عرض حالة وتوزيع الغرف الحالية (اضغط على اسم الغرفة لتعديله مباشرة)</div>
            <div id="alertSection"></div>
            <div class="cinema-grid" id="cinemaGrid"></div>
        </div>
    </div>
</div>

<script>
    // بناء مصفوفة الغرف الافتراضية المطلوبة منك
    let rooms = [];
    rooms.push({ id: "غرفة 1", capacity: 8 });
    rooms.push({ id: "غرفة 2", capacity: 7 });
    for (let i = 1; i <= 13; i++) { rooms.push({ id: `غرفة ${i + 2}`, capacity: 5 }); }
    for (let i = 1; i <= 2; i++) { rooms.push({ id: `غرفة ${i + 15}`, capacity: 4 }); }

    let currentAssignments = {};

    // توليد شاشة السينما للغرف تلقائياً
    function renderCinema() {
        const grid = document.getElementById('cinemaGrid');
        grid.innerHTML = '';
        let totalBeds = 0;

        rooms.forEach((room, index) => {
            totalBeds += room.capacity;
            const data = currentAssignments[room.id] || { guests: [] };
            
            // بناء السراير (المقاعد السينمائية)
            let seatsHTML = '';
            for(let i = 0; i < room.capacity; i++) {
                if(data.guests[i]) {
                    seatsHTML += `<div class="seat occupied">🛏️<span class="tooltip">${data.guests[i]}</span></div>`;
                } else {
                    seatsHTML += `<div class="seat empty"></div>`;
                }
            }

            // بناء قائمة الأسماء الظاهرة أسفل المربع
            let guestsListHTML = '';
            if(data.guests.length > 0) {
                data.guests.forEach(g => {
                    guestsListHTML += `<span class="guest-item">👤 ${g}</span>`;
                });
            } else {
                guestsListHTML += `<span style="color:#64748b; font-size:12px;">غرفة فارغة</span>`;
            }

            // الكارد الكامل للغرفة
            grid.innerHTML += `
                <div class="room-card">
                    <div class="room-header">
                        <input type="text" class="editable-name" value="${room.id}" onchange="renameRoom(${index}, this.value)">
                        <span class="beds-count">${data.guests.length}/${room.capacity} سرير</span>
                    </div>
                    <div class="seats-container">
                        ${seatsHTML}
                    </div>
                    <div class="room-guests-list">
                        ${guestsListHTML}
                    </div>
                    <div class="action-zone">
                        <button class="btn-del-room" onclick="deleteRoom(${index})">❌ حذف الغرفة</button>
                    </div>
                </div>`;
        });

        document.getElementById('totalBedsStats').innerText = `إجمالي الطاقة: ${totalBeds} سرير متاح`;
    }

    // تعديل اسم الغرفة مباشرة من الشاشة
    function renameRoom(index, newName) {
        newName = newName.trim();
        if(!newName) return;
        rooms[index].id = newName;
        startAccommodation(); // إعادة الحساب فورا لتحديث التوزيع ببيانات الاسم الجديد
    }

p
