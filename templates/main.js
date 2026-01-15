// --- UI LOGIC: THREAT CARDS ---
        function selectThreatUI(mode, threatId, colorName) {
            // 1. Update Hidden Input
            document.getElementById(`${mode}ThreatId`).value = threatId;
            
            // 2. Visual Feedback
            const container = document.getElementById(`${mode}ThreatCards`);
            const cards = container.querySelectorAll('.card');
            
            cards.forEach(card => {
                // Check if this card matches the clicked color
                if (card.getAttribute('data-color') === colorName) {
                    card.classList.add('active');
                } else {
                    card.classList.remove('active');
                }
            });
        }

        // --- UPDATED ADD FUNCTION ---
        async function submitAdd() {
            const data = {
                code_name: document.getElementById('addName').value,
                diagnosis: document.getElementById('addDiagnosis').value,
                doctor_id: document.getElementById('addDoctorSelect').value,
                room_id: document.getElementById('addRoomSelect').value,
                threat_id: document.getElementById('addThreatId').value
            };

            if(!data.code_name) return alert("ERROR: IDENTIFIER REQUIRED");

            try {
                const res = await fetch('/api/add_subject', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await res.json();
                if(result.success) {
                    closeModal('add');
                    // Очистка полей
                    document.getElementById('addName').value = '';
                    document.getElementById('addDiagnosis').value = '';
                    fetchData(); // Обновление таблицы
                } else {
                    alert("DATABASE ERROR: " + result.message);
                }
            } catch(e) { console.error(e); }
        }

        // --- UPDATED EDIT OPEN FUNCTION ---
        function openEditModal(id) {
            currentEditId = id;
            const subject = allSubjects.find(s => s.SubjectID === id);
            if (!subject) return;

            document.getElementById('editSubjectId').value = subject.SubjectID;
            document.getElementById('editName').value = subject.CodeName;
            document.getElementById('editDiagnosis').value = subject.Diagnosis || '';
            document.getElementById('editDoctorSelect').value = subject.AssignedDoctorID || '';
            document.getElementById('editRoomSelect').value = subject.AssignedRoomID || '';

            // Установка карточки угрозы
            // Определяем цвет по ThreatName или ID. Предполагаем ID 1-4.
            const tId = subject.AssignedThreatID || 1;
            let color = 'Green';
            if(tId == 2) color = 'Yellow';
            if(tId == 3) color = 'Red';
            if(tId == 4) color = 'Black';
            
            selectThreatUI('edit', tId, color);

            document.getElementById('editModal').classList.remove('hidden');
        }