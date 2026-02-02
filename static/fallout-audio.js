/* ============================================================================ */
/* FALLOUT AUDIO SYSTEM - Web Audio API                                        */
/* Звуки в стиле Fallout: New Vegas / Fallout 4                                */
/* ============================================================================ */

class FalloutAudioManager {
    constructor() {
        this.audioContext = null;
        this.isInitialized = false;
        this.isMuted = false;
        this.volume = 0.3; // 30% громкости по умолчанию
        
        // Инициализируем при первом взаимодействии
        document.addEventListener('click', () => this.initAudioContext(), { once: true });
        document.addEventListener('mousemove', () => this.initAudioContext(), { once: true });
    }
    
    initAudioContext() {
        if (!this.isInitialized) {
            try {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                this.isInitialized = true;
            } catch (e) {
                console.warn('Web Audio API не поддерживается:', e);
            }
        }
    }
    
    /* ===== ОСНОВНЫЕ ЗВУКОВЫЕ ЭФФЕКТЫ ===== */
    
    // Нажатие кнопки - терминальный звук
    playButtonClick() {
        if (!this.isInitialized || this.isMuted) return;
        
        const ctx = this.audioContext;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        osc.frequency.setValueAtTime(880, now); // A5 нота
        osc.frequency.exponentialRampToValueAtTime(440, now + 0.05);
        
        gain.gain.setValueAtTime(this.volume, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.05);
        
        osc.start(now);
        osc.stop(now + 0.05);
    }
    
    // Наведение - мягкий звон
    playHover() {
        if (!this.isInitialized || this.isMuted) return;
        
        const ctx = this.audioContext;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        osc.frequency.setValueAtTime(600, now);
        osc.frequency.exponentialRampToValueAtTime(500, now + 0.03);
        
        gain.gain.setValueAtTime(this.volume * 0.3, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.03);
        
        osc.start(now);
        osc.stop(now + 0.03);
    }
    
    // Скролл - пилящий звук
    playScroll() {
        if (!this.isInitialized || this.isMuted) return;
        
        const ctx = this.audioContext;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        osc.frequency.setValueAtTime(300, now);
        osc.frequency.linearRampToValueAtTime(250, now + 0.08);
        
        gain.gain.setValueAtTime(this.volume * 0.2, now);
        gain.gain.linearRampToValueAtTime(0.01, now + 0.08);
        
        osc.start(now);
        osc.stop(now + 0.08);
    }
    
    // Успешное действие - восходящий звук
    playSuccess() {
        if (!this.isInitialized || this.isMuted) return;
        
        const ctx = this.audioContext;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        // Восходящий звук
        osc.frequency.setValueAtTime(440, now); // A4
        osc.frequency.exponentialRampToValueAtTime(880, now + 0.1); // A5
        osc.frequency.exponentialRampToValueAtTime(1100, now + 0.2); // выше
        
        gain.gain.setValueAtTime(this.volume * 0.4, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
        
        osc.start(now);
        osc.stop(now + 0.2);
    }
    
    // Ошибка - нисходящий звук
    playError() {
        if (!this.isInitialized || this.isMuted) return;
        
        const ctx = this.audioContext;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        // Нисходящий звук
        osc.frequency.setValueAtTime(800, now);
        osc.frequency.exponentialRampToValueAtTime(200, now + 0.15);
        
        gain.gain.setValueAtTime(this.volume * 0.5, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
        
        osc.start(now);
        osc.stop(now + 0.15);
    }
    
    // Загрузка/статическая - шумовой эффект
    playStatic() {
        if (!this.isInitialized || this.isMuted) return;
        
        const ctx = this.audioContext;
        const now = ctx.currentTime;
        const bufferSize = ctx.sampleRate * 0.1; // 100ms
        const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
        const data = buffer.getChannelData(0);
        
        // Заполнить белый шум
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }
        
        const source = ctx.createBufferSource();
        const gain = ctx.createGain();
        
        source.buffer = buffer;
        source.connect(gain);
        gain.connect(ctx.destination);
        
        gain.gain.setValueAtTime(this.volume * 0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
        
        source.start(now);
    }
    
    // Переключение темы - эффект включения
    playThemeSwitch() {
        if (!this.isInitialized || this.isMuted) return;
        
        const ctx = this.audioContext;
        const now = ctx.currentTime;
        
        // Первый звук
        const osc1 = ctx.createOscillator();
        const gain1 = ctx.createGain();
        
        osc1.connect(gain1);
        gain1.connect(ctx.destination);
        
        osc1.frequency.setValueAtTime(440, now);
        osc1.frequency.exponentialRampToValueAtTime(880, now + 0.08);
        
        gain1.gain.setValueAtTime(this.volume * 0.3, now);
        gain1.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
        
        osc1.start(now);
        osc1.stop(now + 0.08);
        
        // Второй звук (параллельный)
        const osc2 = ctx.createOscillator();
        const gain2 = ctx.createGain();
        
        osc2.connect(gain2);
        gain2.connect(ctx.destination);
        
        osc2.frequency.setValueAtTime(550, now + 0.05);
        osc2.frequency.exponentialRampToValueAtTime(1100, now + 0.13);
        
        gain2.gain.setValueAtTime(this.volume * 0.2, now + 0.05);
        gain2.gain.exponentialRampToValueAtTime(0.01, now + 0.13);
        
        osc2.start(now + 0.05);
        osc2.stop(now + 0.13);
    }
    
    // Модальное окно открывается - звук активации
    playModalOpen() {
        if (!this.isInitialized || this.isMuted) return;
        
        const ctx = this.audioContext;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        osc.frequency.setValueAtTime(200, now);
        osc.frequency.exponentialRampToValueAtTime(600, now + 0.12);
        
        gain.gain.setValueAtTime(this.volume * 0.25, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
        
        osc.start(now);
        osc.stop(now + 0.12);
    }
    
    // Модальное окно закрывается - звук деактивации
    playModalClose() {
        if (!this.isInitialized || this.isMuted) return;
        
        const ctx = this.audioContext;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        osc.frequency.setValueAtTime(600, now);
        osc.frequency.exponentialRampToValueAtTime(200, now + 0.12);
        
        gain.gain.setValueAtTime(this.volume * 0.25, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
        
        osc.start(now);
        osc.stop(now + 0.12);
    }
    
    // Радар - характерный пип (как в Fallout)
    playRadar() {
        if (!this.isInitialized || this.isMuted) return;
        
        const ctx = this.audioContext;
        const now = ctx.currentTime;
        
        for (let i = 0; i < 3; i++) {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            
            osc.connect(gain);
            gain.connect(ctx.destination);
            
            const startTime = now + (i * 0.08);
            
            osc.frequency.setValueAtTime(1200 - (i * 150), startTime);
            gain.gain.setValueAtTime(this.volume * 0.2, startTime);
            gain.gain.exponentialRampToValueAtTime(0.01, startTime + 0.05);
            
            osc.start(startTime);
            osc.stop(startTime + 0.05);
        }
    }
    
    /* ===== УПРАВЛЕНИЕ ===== */
    
    setVolume(level) {
        this.volume = Math.max(0, Math.min(1, level));
    }
    
    toggleMute() {
        this.isMuted = !this.isMuted;
        return this.isMuted;
    }
    
    mute() {
        this.isMuted = true;
    }
    
    unmute() {
        this.isMuted = false;
    }
}

// Создание глобального экземпляра
const falloutAudio = new FalloutAudioManager();

// ============================================================================
// ИНТЕГРАЦИЯ ЗВУКОВ С ИНТЕРФЕЙСОМ
// ============================================================================

// Звуки для кнопок
document.addEventListener('DOMContentLoaded', function() {
    // Кнопки
    document.addEventListener('click', function(e) {
        const target = e.target.closest('button, input[type="submit"], input[type="button"], a.btn, .btn');
        if (target) {
            falloutAudio.playButtonClick();
        }
    });
    
    // Наведение мыши на кнопки
    document.addEventListener('mouseover', function(e) {
        if (e.target.closest('button, input[type="submit"], .btn:not(.danger-btn)')) {
            falloutAudio.playHover();
        }
    });
    
    // Скролл
    document.addEventListener('wheel', function(e) {
        if (e.target.closest('.data-panel')) {
            falloutAudio.playScroll();
        }
    }, { passive: true });
    
    // Переключение темы
    const originalToggleTheme = window.toggleTheme;
    if (originalToggleTheme) {
        window.toggleTheme = function() {
            falloutAudio.playThemeSwitch();
            return originalToggleTheme.call(this);
        };
    }
    
    // Модальные окна
    const originalOpenModal = window.openModal;
    if (originalOpenModal) {
        window.openModal = function() {
            falloutAudio.playModalOpen();
            return originalOpenModal.apply(this, arguments);
        };
    }
    
    const originalCloseModal = window.closeModal;
    if (originalCloseModal) {
        window.closeModal = function() {
            falloutAudio.playModalClose();
            return originalCloseModal.apply(this, arguments);
        };
    }
    
    // Входные данные
    document.addEventListener('change', function(e) {
        if (e.target.matches('input, select, textarea')) {
            falloutAudio.playHover();
        }
    });
    
    // Ошибки/успех (если есть элементы с data атрибутами)
    document.addEventListener('click', function(e) {
        if (e.target.getAttribute('data-status') === 'error') {
            falloutAudio.playError();
        } else if (e.target.getAttribute('data-status') === 'success') {
            falloutAudio.playSuccess();
        }
    });
});

// Экспорт для использования в других скриптах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FalloutAudioManager;
}
