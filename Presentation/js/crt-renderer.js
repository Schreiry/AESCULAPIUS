/**
 * AESCULAPIUS CRT RENDERER
 * WebGL-based Post-Processing for that authentic "Heavy Glass" feel.
 * FIXED: Corrected distortion math and vignette logic to prevent black screen.
 */

const CRT_CONFIG = {
    curvature: { x: 0.1, y: 0.1 }, // Safe barrel distortion factor
    scanlines: {
        count: 800.0,
        opacity: 0.1, // Subtle
        speed: 0.05
    },
    vignette: {
        roundness: 0.4, // Not used in new formula, but kept for config
        smoothness: 0.8
    },
    noise: 0.05
};

class CRTRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.gl = this.canvas.getContext('webgl');

        if (!this.gl) {
            console.error("WebGL not supported.");
            return;
        }

        this.program = null;
        this.buffer = null;
        this.startTime = Date.now();

        this.resize();
        window.addEventListener('resize', () => this.resize());

        this.init();
        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        if (this.gl) {
            this.gl.viewport(0, 0, this.canvas.width, this.canvas.height);
        }
    }

    createShader(type, source) {
        const shader = this.gl.createShader(type);
        this.gl.shaderSource(shader, source);
        this.gl.compileShader(shader);

        if (!this.gl.getShaderParameter(shader, this.gl.COMPILE_STATUS)) {
            console.error('Shader compile error:', this.gl.getShaderInfoLog(shader));
            this.gl.deleteShader(shader);
            return null;
        }
        return shader;
    }

    init() {
        const vsSource = `
            attribute vec2 position;
            varying vec2 vUv;
            void main() {
                vUv = position * 0.5 + 0.5;
                gl_Position = vec4(position, 0.0, 1.0);
            }
        `;

        const fsSource = `
            precision mediump float;
            varying vec2 vUv;
            uniform float uTime;
            uniform vec2 uResolution;
            
            // Config Uniforms
            uniform vec2 uCurvature;
            uniform float uScanlineCount;
            uniform float uScanlineOpacity;
            uniform float uNoise;

            // Safe Distortion Function
            vec2 curve(vec2 uv) {
                uv = (uv - 0.5) * 2.0;
                vec2 offset = abs(uv.yx) / vec2(6.0, 4.0); // Aspect ratio correction
                uv = uv + uv * offset * offset;
                uv = uv * 0.5 + 0.5;
                return uv;
            }

            // Random Noise
            float random(vec2 st) {
                return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
            }

            void main() {
                vec2 uv = curve(vUv);
                
                // 1. Edge Clamping (Black border)
                if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
                    gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
                    return;
                }

                // 2. Scanlines
                // High frequency fine lines
                float s1 = sin(uv.y * uScanlineCount + uTime * 5.0);
                // Low frequency rolling bar
                float s2 = sin(uv.y * 10.0 - uTime * 2.0);
                
                float scanline = (s1 * 0.5 + s2 * 0.1); 
                
                // 3. Vignette (Rounded Rectangle)
                vec2 d = abs((uv - 0.5) * 2.0);
                // x^8 + y^8 creates a squircle (TV shape)
                float vigDist = pow(d.x, 8.0) + pow(d.y, 8.0);
                float vig = smoothstep(0.8, 1.2, vigDist); // 0 at center, 1 at edges

                // 4. Noise
                float noiseVal = random(uv * uTime) * uNoise;
                
                // 5. Compose
                // We want to DARKEN the screen at edges (Vignette) and on Scanlines.
                // We want to ADD noise.
                
                // Alpha for darkening layers
                float darkAlpha = vig + (1.0 - (s1 * 0.5 + 0.5)) * uScanlineOpacity;
                
                // Clamp alpha
                darkAlpha = clamp(darkAlpha, 0.0, 1.0);
                
                // Output:
                // RGB = Noise (Greenish)
                // Alpha = Darkening + Noise Opacity
                
                gl_FragColor = vec4(0.0, noiseVal * 0.5, 0.0, darkAlpha + noiseVal * 0.1);
            }
        `;

        const vertexShader = this.createShader(this.gl.VERTEX_SHADER, vsSource);
        const fragmentShader = this.createShader(this.gl.FRAGMENT_SHADER, fsSource);

        this.program = this.gl.createProgram();
        this.gl.attachShader(this.program, vertexShader);
        this.gl.attachShader(this.program, fragmentShader);
        this.gl.linkProgram(this.program);

        if (!this.gl.getProgramParameter(this.program, this.gl.LINK_STATUS)) {
            console.error('Shader link error:', this.gl.getProgramInfoLog(this.program));
            return;
        }

        // Buffer Setup
        const positions = new Float32Array([
            -1.0, -1.0,
            1.0, -1.0,
            -1.0, 1.0,
            1.0, 1.0,
        ]);

        this.buffer = this.gl.createBuffer();
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.buffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, positions, this.gl.STATIC_DRAW);

        // Uniform Locations
        this.uTime = this.gl.getUniformLocation(this.program, 'uTime');
        this.uResolution = this.gl.getUniformLocation(this.program, 'uResolution');
        this.uCurvature = this.gl.getUniformLocation(this.program, 'uCurvature');
        this.uScanlineCount = this.gl.getUniformLocation(this.program, 'uScanlineCount');
        this.uScanlineOpacity = this.gl.getUniformLocation(this.program, 'uScanlineOpacity');
        this.uNoise = this.gl.getUniformLocation(this.program, 'uNoise');
    }

    animate() {
        if (!this.gl || !this.program) return;

        const time = (Date.now() - this.startTime) * 0.001;

        this.gl.useProgram(this.program);

        // Bind Buffer
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.buffer);
        const positionLocation = this.gl.getAttribLocation(this.program, 'position');
        this.gl.enableVertexAttribArray(positionLocation);
        this.gl.vertexAttribPointer(positionLocation, 2, this.gl.FLOAT, false, 0, 0);

        // Set Uniforms
        this.gl.uniform1f(this.uTime, time);
        this.gl.uniform2f(this.uResolution, this.canvas.width, this.canvas.height);
        this.gl.uniform2f(this.uCurvature, CRT_CONFIG.curvature.x, CRT_CONFIG.curvature.y);
        this.gl.uniform1f(this.uScanlineCount, CRT_CONFIG.scanlines.count);
        this.gl.uniform1f(this.uScanlineOpacity, CRT_CONFIG.scanlines.opacity);
        this.gl.uniform1f(this.uNoise, CRT_CONFIG.noise);

        // Draw
        this.gl.drawArrays(this.gl.TRIANGLE_STRIP, 0, 4);

        requestAnimationFrame(() => this.animate());
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    new CRTRenderer('crt-canvas');
});
