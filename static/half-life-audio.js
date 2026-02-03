/* ============================================================================ */
/* HALF-LIFE AUDIO SYSTEM - Valve Audio Integration                           */
/* Интеграция звуков Half-Life для AESCULAPIUS                                */
/* ============================================================================ */

class HalfLifeAudioManager {
    constructor() {
        // Audio files paths (в папке /static/sound/)
        this.sounds = {
            buttonClick: '/static/sound/knopka-iz-igry-2.mp3',
            buttonDelete: '/static/sound/knopka-ispolzovaniia-e.mp3',
            hoverRow: '/static/sound/vybor-rezhima.mp3',
            accessDenied: '/static/sound/access-denied_Is238Ly.mp3',
            mainTheme: '/static/sound/06. No Rest for These Bones.mp3'
        };
        
        this.audioElements = {};
        this.isMuted = false;
        this.volume = 1.0;
        this.isInitialized = false;
        
        // Фоновая музыка
        this.bgMusicPlaying = false;
        this.bgMusicElement = null;
        
        // Throttle для hover звуков (чтобы не производить слишком много звуков)
        this.lastHoverTime = 0;
        this.hoverThrottle = 150; // мс между hover звуками
        
        // Инициализация при первом взаимодействии
        document.addEventListener('click', () => this.init(), { once: true });
        document.addEventListener('mousemove', () => this.init(), { once: true });
    }
    
    init() {
        if (this.isInitialized) return;
        this.isInitialized = true;
        this.createAudioElements();
        // НЕ пытаемся автозапустить музыку - браузеры блокируют
        // Музыка только по явной команде юзера
    }
    
    createAudioElements() {
        // Создаём audio элементы для каждого звука
        for (const [key, path] of Object.entries(this.sounds)) {
            const audio = document.createElement('audio');
            audio.src = path;
            audio.volume = this.volume;
            
            // Для фоновой музыки
            if (key === 'mainTheme') {
                audio.loop = true;
                audio.preload = 'auto';
                audio.style.display = 'none';
            } else {
                audio.preload = 'auto';
            }
            
            document.body.appendChild(audio);
            this.audioElements[key] = audio;
        }
    }
    
    playSound(soundKey, { force = false, offset = 0, fadeOut = false } = {}) {
        if (this.isMuted && !force) return;
        
        const audio = this.audioElements[soundKey];
        if (!audio) {
            console.warn(`Sound not found: ${soundKey}`);
            return;
        }
        
        try {
            // Останавливаем предыдущее воспроизведение
            audio.currentTime = offset;
            
            // Если нужно затухание звука
            if (fadeOut) {
                // Плавное затухание для hover звуков
                const originalVolume = this.volume;
                audio.volume = originalVolume;
                audio.play().catch(e => {
                    // Браузер может заблокировать autoplay
                    console.log('Autoplay blocked or error:', e);
                });
                
                // Мягкое затухание после начала
                setTimeout(() => {
                    if (audio.currentTime > 0) {
                        const fadeStart = audio.currentTime;
                        const fadeDuration = 0.2; // 200ms затухание
                        const startVolume = audio.volume;
                        const startTime = Date.now();
                        
                        const fadeInterval = setInterval(() => {
                            const elapsed = (Date.now() - startTime) / 1000;
                            if (elapsed >= fadeDuration) {
                                audio.volume = 0;
                                clearInterval(fadeInterval);
                            } else {
                                audio.volume = startVolume * (1 - elapsed / fadeDuration);
                            }
                        }, 10);
                    }
                }, 100);
            } else {
                audio.volume = this.volume;
                audio.play().catch(e => {
                    console.log('Autoplay blocked or error:', e);
                });
            }
        } catch (e) {
            console.error(`Error playing sound ${soundKey}:`, e);
        }
    }
    
    startBackgroundMusic() {
        if (!this.audioElements['mainTheme']) return;
        
        const bgMusic = this.audioElements['mainTheme'];
        
        if (!this.bgMusicPlaying) {
            bgMusic.volume = 0.4; // Фоновая музыка тише основных звуков
            bgMusic.play().catch(e => {
                console.log('Background music autoplay blocked:', e);
            });
            this.bgMusicPlaying = true;
        }
    }
    
    stopBackgroundMusic() {
        if (this.audioElements['mainTheme']) {
            this.audioElements['mainTheme'].pause();
            this.bgMusicPlaying = false;
        }
    }
    
    playButtonClick() {
        this.playSound('buttonClick');
    }
    
    playButtonDelete() {
        this.playSound('buttonDelete');
    }
    
    playHoverRow() {
        const now = Date.now();
        if (now - this.lastHoverTime > this.hoverThrottle) {
            this.playSound('hoverRow', { fadeOut: true });
            this.lastHoverTime = now;
        }
    }
    
    playAccessDenied() {
        this.playSound('accessDenied', { force: true });
    }
    
    setVolume(level) {
        this.volume = Math.max(0, Math.min(1, level));
        
        for (const audio of Object.values(this.audioElements)) {
            if (audio !== this.audioElements['mainTheme']) {
                audio.volume = this.volume;
            }
        }
        
        // Background music volume зависит от основного volume
        if (this.audioElements['mainTheme']) {
            this.audioElements['mainTheme'].volume = this.volume * 0.4;
        }
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
const halfLifeAudio = new HalfLifeAudioManager();

// ============================================================================
// ИНТЕГРАЦИЯ ЗВУКОВ С ИНТЕРФЕЙСОМ
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // === КНОПКИ - основные звуки ===
    document.addEventListener('click', function(e) {
        const target = e.target.closest('button, input[type="submit"], input[type="button"], .btn:not(.delete-btn), a.btn');
        if (target && !target.classList.contains('delete-btn')) {
            halfLifeAudio.playButtonClick();
        }
    });
    
    // === КНОПКИ УДАЛЕНИЯ - специальный звук ===
    document.addEventListener('click', function(e) {
        const target = e.target.closest('.delete-btn, .mini-btn.delete-btn, button[data-action="delete"], [class*="delete"]');
        if (target) {
            halfLifeAudio.playButtonDelete();
        }
    });
    
    // === НАВЕДЕНИЕ НА СТРОКИ ТАБЛИЦЫ - hover звук с затуханием ===
    document.addEventListener('mouseover', function(e) {
        const row = e.target.closest('tr');
        if (row && row.closest('table')) {
            halfLifeAudio.playHoverRow();
        }
    });
    
    // === СКРОЛЛ ТАБЛИЦЫ - умный звук прокрутки ===
    const dataPanel = document.querySelector('.data-panel');
    if (dataPanel) {
        let lastScrollTime = 0;
        const scrollThrottle = 200; // мс между звуками прокрутки
        
        dataPanel.addEventListener('scroll', function() {
            const now = Date.now();
            // Воспроизводим только одного hover звука каждые 200ms
            // Это создаёт мягкий, непрерывный звук прокрутки
            if (now - lastScrollTime > scrollThrottle) {
                halfLifeAudio.playHoverRow();
                lastScrollTime = now;
            }
        }, { passive: true });
    }
    
    // === НЕВЕРНЫЙ ПАРОЛЬ - звук доступа запрещён ===
    // Проверяем на странице логина при ошибке
    const checkForAuthError = () => {
        const errorMsg = document.querySelector('.error-msg');
        if (errorMsg && (errorMsg.textContent.includes('Invalid') || errorMsg.textContent.includes('incorrect') || errorMsg.textContent.includes('ERROR'))) {
            halfLifeAudio.playAccessDenied();
        }
    };
    
    // При отправке формы логина
    const loginForm = document.querySelector('form');
    if (loginForm) {
        loginForm.addEventListener('submit', function() {
            setTimeout(checkForAuthError, 500);
        });
    }
});

// При загрузке страницы - НЕ пытаемся автозапустить фоновую музыку
// Браузеры блокируют autoplay звука без явного user gesture
// Музыка будет воспроизводиться только по явному действию пользователя

// Экспорт для использования в других скриптах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HalfLifeAudioManager;
}
