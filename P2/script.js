// Función para mostrar u ocultar los campos
function toggleCampos() {
    const modo = document.getElementById('modoOperacion').value;

    // Seleccionamos los contenedores completos
    const grupoX2 = document.getElementById('grupo-x2');
    const grupoY2 = document.getElementById('grupo-y2');
    
    // Inputs individuales
    const x2 = document.getElementById('x2');
    const y2 = document.getElementById('y2');

    // Validación por si aún no carga el HTML
    if (!grupoX2 || !grupoY2) return;

    if (modo === "doblado") {
        // Ocultar los campos por completo
        grupoX2.style.display = 'none';
        grupoY2.style.display = 'none';
        
        // Limpiar los valores
        x2.value = '';
        y2.value = '';
    } else {
        // Mostrar los campos nuevamente
        grupoX2.style.display = 'flex';
        grupoY2.style.display = 'flex';
    }
}

// Ejecutar cuando se cambie la opción en el menú
document.getElementById('modoOperacion').addEventListener('change', toggleCampos);

// Ejecutar al cargar la página (por si el navegador recuerda la opción "doblado")
window.addEventListener('DOMContentLoaded', toggleCampos);
/* =====================================================
   ARITMÉTICA MODULAR
   ===================================================== */

/** Módulo garantizado positivo */
function mod(a, m) { return ((a % m) + m) % m; }

/** Exponenciación modular rápida: base^exp mod m */
function modPow(base, exp, m) {
    if (m === 1) return 0;
    let result = 1;
    base = mod(base, m);
    while (exp > 0) {
        if (exp % 2 === 1) result = mod(result * base, m);
        exp = Math.floor(exp / 2);
        base = mod(base * base, m);
    }
    return result;
}

/** Verifica si n es primo */
function isPrime(n) {
    if (n < 2) return false;
    if (n === 2) return true;
    if (n % 2 === 0) return false;
    for (let i = 3; i * i <= n; i += 2)
        if (n % i === 0) return false;
    return true;
}

/* =====================================================
   UTILIDADES DE UI
   ===================================================== */

function setMsg(type, icon, html) {
    document.getElementById('msgArea').innerHTML =
        `<div class="msg msg-${type}"><i class="fas ${icon}"></i><span>${html}</span></div>`;
}
function clearMsg() { document.getElementById('msgArea').innerHTML = ''; }

function setPreset(a, b, p) {
    document.getElementById('inputA').value = a;
    document.getElementById('inputB').value = b;
    document.getElementById('inputP').value = p;
    runCalc();
}

/** Actualiza la fórmula dinámica en el hero */
function updateFormula(a, b, p) {
    const aStr = a === 0 ? '' : (a > 0 ? ` + ${a}x` : ` − ${Math.abs(a)}x`);
    const bStr = b === 0 ? '' : (b > 0 ? ` + ${b}` : ` − ${Math.abs(b)}`);
    document.getElementById('formulaDynamic').textContent =
        `y² ≡ x³${aStr}${bStr}  (mod ${p})`;
}

/* =====================================================
   CÁLCULO PRINCIPAL
   ===================================================== */

function runCalc() {
    clearMsg();
    document.getElementById('resultsSection').classList.remove('show');

    const a = parseInt(document.getElementById('inputA').value);
    const b = parseInt(document.getElementById('inputB').value);
    const p = parseInt(document.getElementById('inputP').value);

    // ---- Validaciones ----
    if (isNaN(a) || isNaN(b) || isNaN(p)) {
        setMsg('err', 'fa-exclamation-circle', 'Ingresa valores numéricos válidos para a, b y p.');
        return;
    }
    if (p < 2) {
        setMsg('err', 'fa-exclamation-circle', 'p debe ser ≥ 2.');
        return;
    }
    if (!isPrime(p)) {
        setMsg('err', 'fa-exclamation-circle',
            `p = ${p} <strong>no es primo</strong>. Las curvas elípticas sobre F<sub>p</sub> requieren p primo.`);
        return;
    }
    if (p > 150) {
        console.log("Ingreso a 150");
        setMsg('warn', 'fa-exclamation-triangle',
            `p = ${p} es relativamente grande. Las tablas serán largas (${p} filas).`);
        return
    }

    updateFormula(a, b, p);

    // ---- PASO 1: Discriminante Δ = 4a³ + 27b² mod p ----
    const aMP  = mod(a, p);
    const bMP  = mod(b, p);
    const a3   = modPow(aMP, 3, p);
    const b2   = mod(bMP * bMP, p);
    const t1   = mod(4 * a3, p);
    const t2   = mod(27 * b2, p);
    const disc = mod(t1 + t2, p);
    const valid = disc !== 0;

    // ---- PASO 2: z = x³ + ax + b mod p ----
    const zRows = [];
    for (let x = 0; x < p; x++) {
        const x3r  = x * x * x;          // x³ crudo
        const axr  = a * x;              // ax crudo
        const raw  = x3r + axr + b;      // suma cruda (para mostrar)
        const z    = mod(raw, p);
        // Para mostrar el paso modular de x³ (en caso de x³ > p)
        const x3mp = mod(x3r, p);
        const axmp = mod(axr, p);
        const bmp  = mod(b, p);
        zRows.push({ x, x3r, axr, raw, z, x3mp, axmp, bmp });
    }

    // ---- PASO 3: y² mod p ----
    const yRows = [];
    for (let y = 0; y < p; y++) {
        const y2r = y * y;
        const y2  = mod(y2r, p);
        yRows.push({ y, y2r, y2 });
    }

    // ---- PASO 4: Encontrar puntos ----
    const points = [];
    for (let x = 0; x < p; x++)
        for (let y = 0; y < p; y++)
            if (yRows[y].y2 === zRows[x].z)
                points.push([x, y]);

    // ---- RENDER ----

    if (!valid) {
        setMsg('err', 'fa-times-circle',
            `La curva es <strong>singular</strong> (Δ = 0). El discriminante es cero: no define un grupo válido.`);
        } else {
            setMsg('ok', 'fa-check-circle',
                `Curva <strong>válida</strong> (Δ = ${disc} ≠ 0). Se encontraron <strong>${points.length}</strong> punto(s) afín(es) + ∞ → <strong>|E| = ${points.length + 1}</strong>`);
            renderDisc(a, b, p, aMP, bMP, a3, b2, t1, t2, disc, valid);
            renderTableZ(a, b, p, zRows, points);
            renderTableY(p, yRows, points);
            renderMatch(zRows, yRows, points, p);
            renderSet(points, p);
            document.getElementById('resultsSection').classList.add('show');
        }
}

/* =====================================================
   RENDER – PASO 1: DISCRIMINANTE
   ===================================================== */

function renderDisc(a, b, p, aMP, bMP, a3, b2, t1, t2, disc, valid) {
    const aMath = a !== aMP ? `${a} ≡ <span class="hl">${aMP}</span> (mod ${p})` : `<span class="hl">${aMP}</span>`;
    const bMath = b !== bMP ? `${b} ≡ <span class="hl">${bMP}</span> (mod ${p})` : `<span class="hl">${bMP}</span>`;

    document.getElementById('discBox').innerHTML = `
<div>Condición de curva válida: &nbsp;<strong>4a³ + 27b² ≢ 0 (mod p)</strong></div>
<hr class="disc-sep">
<div>a mod ${p} &nbsp;= ${aMath}</div>
<div>b mod ${p} &nbsp;= ${bMath}</div>
<hr class="disc-sep">
<div>a³ mod ${p} &nbsp;= ${aMP}³ mod ${p} = ${Math.pow(aMP,3)} mod ${p} = <span class="hl">${a3}</span></div>
<div>b² mod ${p} &nbsp;= ${bMP}² mod ${p} = ${bMP*bMP} mod ${p} = <span class="hl">${b2}</span></div>
<hr class="disc-sep">
<div>4 × ${a3} = ${4*a3} &nbsp;→ &nbsp;<strong>4a³ mod ${p}</strong> = <span class="hl">${t1}</span></div>
<div>27 × ${b2} = ${27*b2} &nbsp;→ &nbsp;<strong>27b² mod ${p}</strong> = <span class="hl">${t2}</span></div>
<hr class="disc-sep">
<div>Δ = ${t1} + ${t2} = ${t1+t2} mod ${p} = <span class="hl2">${disc}</span></div>
<div>
    <span class="valid-chip ${valid?'chip-ok':'chip-err'}">
        <i class="fas ${valid?'fa-check':'fa-times'}"></i>
        ${valid ? `Curva VÁLIDA (Δ = ${disc} ≠ 0)` : `Curva INVÁLIDA (Δ = 0 — singularidad)`}
    </span>
</div>`;
}

/* =====================================================
   RENDER – PASO 2: TABLA Z
   ===================================================== */

function renderTableZ(a, b, p, zRows, points) {
    const matchXs = new Set(points.map(([x]) => x));

    // Encabezado con la ecuación específica
    const aDisp = a === 0 ? '' : (a > 0 ? ` + ${a}x` : ` − ${Math.abs(a)}x`);
    const bDisp = b === 0 ? '' : (b > 0 ? ` + ${b}` : ` − ${Math.abs(b)}`);

    let html = `<table>
<thead><tr>
    <th>x</th>
    <th>x³${aDisp}${bDisp} &nbsp;(sustitución)</th>
    <th>= Σ</th>
    <th>z mod ${p}</th>
    <th>✓</th>
</tr></thead><tbody>`;

    for (const r of zRows) {
        const { x, x3r, axr, raw, z } = r;
        const match = matchXs.has(x);
        const cls   = match ? 'row-match' : '';

        // Construir string de cálculo detallado
        const axAbs = Math.abs(axr);
        const bAbs  = Math.abs(b);
        let step1, step2;

        // Paso 1: sustitución simbólica → x³ ± |a|·x ± |b|
        const s2 = a === 0 ? '' : (axr >= 0 ? ` + ${axAbs}` : ` − ${axAbs}`);
        const s3 = b === 0 ? '' : (b  >= 0  ? ` + ${bAbs}`  : ` − ${bAbs}`);
        step1 = `${x3r}${s2}${s3}`;
        step2 = raw;

        // Mostrar cálculo detallado con superíndice
        const calcStr = `${x}³${aDisp.replace('x',`·${x}`)}${bDisp} &nbsp;= &nbsp;${step1} &nbsp;= &nbsp;${step2}`;

        html += `<tr class="${cls}">
    <td class="col-id">${x}</td>
    <td class="col-calc">${calcStr}</td>
    <td class="col-raw">${raw}</td>
    <td class="col-mod">${z}</td>
    <td class="col-tick">${match ? '<span style="color:#4ade80">✓</span>' : '<span style="color:#3a5a6a">—</span>'}</td>
</tr>`;
    }

    html += '</tbody></table>';
    document.getElementById('tableZWrap').innerHTML = html;
}

/* =====================================================
   RENDER – PASO 3: TABLA Y²
   ===================================================== */

function renderTableY(p, yRows, points) {
    const matchYs = new Set(points.map(([, y]) => y));

    let html = `<table>
<thead><tr>
    <th>y</th>
    <th>y² &nbsp;(cálculo)</th>
    <th>= y²</th>
    <th>y² mod ${p}</th>
    <th>✓</th>
</tr></thead><tbody>`;

    for (const r of yRows) {
        const { y, y2r, y2 } = r;
        const match = matchYs.has(y);
        const cls   = match ? 'row-match' : '';

        html += `<tr class="${cls}">
    <td class="col-id">${y}</td>
    <td class="col-calc">${y}² &nbsp;= &nbsp;${y} × ${y}</td>
    <td class="col-raw">${y2r}</td>
    <td class="col-mod">${y2}</td>
    <td class="col-tick">${match ? '<span style="color:#4ade80">✓</span>' : '<span style="color:#3a5a6a">—</span>'}</td>
</tr>`;
    }

    html += '</tbody></table>';
    document.getElementById('tableYWrap').innerHTML = html;
}

/* =====================================================
   RENDER – PASO 4: COINCIDENCIAS
   ===================================================== */

function renderMatch(zRows, yRows, points, p) {
    const wrap = document.getElementById('matchWrap');

    if (points.length === 0) {
        wrap.innerHTML = `<div class="no-points-msg">
            <i class="fas fa-search" style="font-size:28px;color:#3a5a6a;margin-bottom:10px;display:block;"></i>
            No se encontraron puntos afines.<br>
            <small style="color:#4a7a90;">Solo existe el punto al infinito ∞.</small>
        </div>`;
        return;
    }

    let html = `<p class="match-intro">
        Se comparan los valores <strong style="color:var(--turquoise)">z(x)</strong> de la Tabla 2
        contra los valores <strong style="color:var(--aqua-light)">y²(y)</strong> de la Tabla 3.
        Cuando coinciden, el par <strong>(x, y)</strong> pertenece a la curva.
    </p>
    <div class="table-scroll">
    <table>
    <thead><tr>
        <th>x</th>
        <th>z(x) mod ${p}</th>
        <th>y</th>
        <th>y²(y) mod ${p}</th>
        <th>¿Coincide?</th>
        <th>Punto de E</th>
    </tr></thead><tbody>`;

    for (const [x, y] of points) {
        const zv  = zRows[x].z;
        const y2v = yRows[y].y2;
        html += `<tr class="row-match">
    <td class="col-id">${x}</td>
    <td class="col-mod">${zv}</td>
    <td class="col-id">${y}</td>
    <td class="col-mod">${y2v}</td>
    <td style="color:#4ade80;font-weight:700;">✓ &nbsp;${zv} = ${y2v}</td>
    <td style="color:var(--turquoise);font-family:'Courier New',monospace;font-weight:700;">(${x}, ${y})</td>
</tr>`;
    }

    html += '</tbody></table></div>';
    wrap.innerHTML = html;
}

/* =====================================================
   RENDER – PASO 5: CONJUNTO E Y CARDINALIDAD
   ===================================================== */

function renderSet(points, p) {
    // Badges de puntos
    let flow = `<span class="pt-badge infinity">∞ &nbsp;(punto al infinito)</span>`;
    for (const [x, y] of points)
        flow += `<span class="pt-badge">(${x}, ${y})</span>`;
    document.getElementById('pointsFlow').innerHTML = flow;

    // Cardinalidad
    const total = points.length + 1;
    document.getElementById('cardVal').textContent = total;
    document.getElementById('cardSub').innerHTML =
        `${points.length} punto(s) afín(es) + 1 punto al infinito (∞) = <strong>${total}</strong> &nbsp;·&nbsp; |E| = ${total}`;
}

/* =====================================================
   INVERSO MODULAR
   ===================================================== */
function modInverse(a, m) {
    a = mod(a, m);
    for (let x = 1; x < m; x++) {
        if (mod(a * x, m) === 1) return x;
    }
    return null;
}

/* =====================================================
   SUMA DE PUNTOS
   ===================================================== */
function sumarPuntos() {
    const x1 = parseInt(document.getElementById('x1').value);
    const y1 = parseInt(document.getElementById('y1').value);
    const x2 = parseInt(document.getElementById('x2').value);
    const y2 = parseInt(document.getElementById('y2').value);
    const p  = parseInt(document.getElementById('inputP').value);
    const a  = parseInt(document.getElementById('inputA').value);
    const modo = document.getElementById('modoOperacion').value;

    if ([x1,y1,p,a].some(v => isNaN(v))) {
        document.getElementById('sumResult').innerHTML =
            `<div class="msg msg-err"><i class="fas fa-exclamation-circle"></i><span>Completa todos los valores (incluyendo p y a).</span></div>`;
        return;
    }

    let lambda;

    // =========================
    // SUMA NORMAL
    // =========================
    if (modo === "suma") {

        if ([x2,y2].some(v => isNaN(v))) {
            document.getElementById('sumResult').innerHTML =
                `<div class="msg msg-err"><i class="fas fa-exclamation-circle"></i><span>Falta P₂.</span></div>`;
            return;
        }

        let num = mod(y2 - y1, p);
        let den = mod(x2 - x1, p);

        let inv = modInverse(den, p);
        if (inv === null) {
            document.getElementById('sumResult').innerHTML =
                `<div class="msg msg-err"><i class="fas fa-info-circle"></i><span>Resultado: ∞ (recta vertical)</span></div>`;
            return;
        }

        lambda = mod(num * inv, p);

        let x3 = mod(lambda * lambda - x1 - x2, p);
        let y3 = mod(lambda * (x1 - x3) - y1, p);

        document.getElementById('sumResult').innerHTML = `
            <div class="msg msg-ok">
                <i class="fas fa-check-circle" style="margin-top: 4px;"></i>
                <div style="width: 100%;">
                    <strong style="color: #86efac; font-size: 15px;">Suma de puntos</strong>
                    <hr style="border:none; border-top:1px solid rgba(74,222,128,0.2); margin: 8px 0;">
                    <span style="font-family: 'Courier New', monospace; color: #b8d8ec;">
                        λ = (${y2} - ${y1}) / (${x2} - ${x1}) mod ${p}<br>
                        λ = ${num} * ${inv} mod ${p} = <strong style="color: var(--gold); font-size: 15px;">${lambda}</strong><br><br>
                        x₃ = ${x3}<br>
                        y₃ = ${y3}<br><br>
                    </span>
                    <strong style="color: var(--turquoise); font-size: 15px;">P₃ = (${x3}, ${y3})</strong>
                </div>
            </div>
        `;
    }

    // =========================
    // DOBLADO
    // =========================
    else {

        let numRaw = 3 * x1 * x1 + a;
        let denRaw = 2 * y1;

        let num = mod(numRaw, p);
        let den = mod(denRaw, p);

        let inv = modInverse(den, p);

        if (inv === null) {
            document.getElementById('sumResult').innerHTML =
                `<div class="msg msg-err"><i class="fas fa-info-circle"></i><span>Resultado: ∞ (tangente vertical)</span></div>`;
            return;
        }

        lambda = mod(num * inv, p);

        let x3 = mod(lambda * lambda - 2 * x1, p);
        let y3 = mod(lambda * (x1 - x3) - y1, p);

        document.getElementById('sumResult').innerHTML = `
            <div class="msg msg-ok">
                <i class="fas fa-check-circle" style="margin-top: 4px;"></i>
                <div style="width: 100%;">
                    <strong style="color: #86efac; font-size: 15px;">Doblado de punto (2P)</strong>
                    <hr style="border:none; border-top:1px solid rgba(74,222,128,0.2); margin: 8px 0;">
                    <span style="font-family: 'Courier New', monospace; color: #b8d8ec;">
                        λ = (3(${x1})² + ${a}) / (2(${y1})) mod ${p}<br>
                        λ = ${num} * ${inv} mod ${p} = <strong style="color: var(--gold); font-size: 15px;">${lambda}</strong><br><br>
                        x₃ = ${x3}<br>
                        y₃ = ${y3}<br><br>
                    </span>
                    <strong style="color: var(--turquoise); font-size: 15px;">2P = (${x3}, ${y3})</strong>
                </div>
            </div>
        `;
    }
}