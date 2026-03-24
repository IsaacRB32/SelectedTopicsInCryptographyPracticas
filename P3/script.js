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
    

let error = document.getElementById("mensajeError");
//let error1 = document.getElementById("mensajeError1");
error.style.display = "none";
let operaciones = document.getElementById("calcularDobladoPuntos");
operaciones.style.display = "none";
function CalcularMultiplicacionEscalar(){
        // Obtiene los valores de las casillas
        let p = document.getElementById("n").value;
        let a = document.getElementById("inputA").value;
        let b = document.getElementById("inputB").value;
        let n = document.getElementById("inputP").value;
        let x1 = document.getElementById("x1_esc").value;
        let y1 = document.getElementById("y1_esc").value;
        document.getElementById("contenedorDoblado").style.display = "none";
        document.getElementById("contenedorSuma").style.display = "none";
        let potencias = [];
        let exponente = 0;
        let x1Temp = x1;
        let y1Temp = y1;
        p = Number(p);
        a = Number(a);
        b = Number(b);
        n = Number(n);
        x1 = Number(x1);
        y1 = Number(y1);
        let contadorDoblados = 0;
        let contadorSumas = 0;
        let contadorTotal = 1;
        let valoresX = [];
        let valoresY = [];
        let i = 0;
        let j = 0;
        if(p==1){
            contadorSumas++;
        }else{
            /*while(contadorTotal!=p){
                contadorTotal = 2*contadorTotal;
                if(contadorTotal>p){
                    contadorSumas++;
                    contadorTotal = contadorTotal/2;
                    contadorTotal = contadorTotal+1;
                }else if(contadorTotal<p){
                    contadorDoblados++;
                }else{
                    contadorDoblados++;
                }
            }*/
           let numeroPotencia=0;
           let pTemp = p;
           while(pTemp>0){
            if(pTemp%2==1){
                potencias.push(exponente);
            }
            pTemp = Math.floor(pTemp/2);
            exponente++;
           }
           console.log(potencias);
        }
        
        for(i=0;i<potencias.length;i++){
            if(potencias[i]!=0){
                //for(j=0;j<potencias[i];j++){
                    document.getElementById("contenedorDoblado").style.display = "block";
                    [x1Temp,y1Temp] = CalcularDobladoPuntos(a,b,n,x1,y1,potencias[i]);
                    valoresX.push(x1Temp);
                    valoresY.push(y1Temp);
                //}
            }else{
                valoresX.push(x1);
                valoresY.push(y1);
            }
        }

        console.log(valoresX);
        console.log(valoresY);

        for(i=0;i<(valoresX.length)-1;i++){
            document.getElementById("contenedorSuma").style.display = "block";
            CalcularSumaPuntos(n,valoresX,valoresY,potencias);
        }

        
        
        //for(i=0;i<contadorDoblados;i++){
            //[x1Temp,y1Temp] = CalcularDobladoPuntos(a,b,n,x1,y1,contadorDoblados);

            //}

        //for(i=0;i<contadorSumas;i++){
            //CalcularSumaPuntos(n,x1,y1,x1Temp,y1Temp,contadorSumas,contadorDoblados);
        //}

        function CalcularDobladoPuntos(a,b,n,x1,y1,contadorDoblados){
            a = Number(a);
            b = Number(b);
            n = Number(n);
            x1 = Number(x1);
            y1 = Number(y1);
            contadorDoblados = Number(contadorDoblados);

            let procedimientoHTML = "";
            let x3Positivo;
            let y3Positivo;

            for (let i = 0; i < contadorDoblados; i++) {
                let valorIteracion = 2**(i+1);
                procedimientoHTML += `<div class="final-point" id="valorFinalPunto"><b>${valorIteracion} P</b></div>`;
                // Obtiene los valores de las casillas
                // Se calcula el inverso aditivo
                let x1Temp;
                let y1Temp;
                // Se calcula el inverso aditivo por si hay un valor negativo
                if(x1<0){
                    x1 = Math.abs(x1);
                    x1Temp = n - (x1%n);
                }else{
                    x1Temp = x1;
                }
                if(y1<0){
                    y1 = Math.abs(y1);
                    y1Temp = n - (y1%n);
                }else{
                    y1Temp = y1;
                }
                
                // Error si n es menor o igual a 0
                if(n<=0){
                    //let error = document.getElementById("mensajeError");
                    //error.innerHTML = "El valor de n no puede ser menor o igual a cero";
                    //error.style.display = "block";
                    operaciones.style.display = "none";
                }else{
                    //let error = document.getElementById("mensajeError");
                    //error.style.display = "none";
                    operaciones.style.display = "none";
                    // Calcula el numerador y el denominador 
                    let numerador = 3*(x1Temp*x1Temp)+a;
                    let denominador = 2*y1Temp;
                    let numeradorPositivo;
                    let denominadorPositivo;
                    numeradorPositivo = numerador;       
                    // Se calcula el inverso aditivo si el denominador es menor a cero
                    if(denominador<0){
                        denominador = Math.abs(denominador);
                        denominadorPositivo = n - (denominador%n);
                    }else{
                        denominadorPositivo = denominador;
                    }
                    // Error si el numerador es 0
                    if(denominador == 0){
                        error.innerHTML = "El numerador es cero";
                        error.style.display = "block";
                    }else{
                        operaciones.style.display = "block";
                        // Texto inicial de lambda
                        procedimientoHTML += `<div class="lambda-box" id="lambda"><b>λ</b> (lambda) = (3x<sub>1</sub><sup>2</sup> + a)/(2y<sub>1</sub>) = [3*(${x1Temp})<sup>2</sup> + ${a}]/(2*${y1Temp}) = (${numeradorPositivo})/(${denominadorPositivo}) = (${numeradorPositivo}) * (${denominadorPositivo})<sup>-1</sup></div>`;
                        // Tabla del algoritmo extendido de Euclides
                        procedimientoHTML += `<h4 class="procedure-subtitle" id="tituloTablas"><b>Algoritmo extendido de Euclides</b></h4>`;
                        // Se realiza el algoritmo extendido de Euclides
                        //let inversoDenominador = AlgoritmoExtendidoEuclides(denominadorPositivo,n,procedimientoHTML);
                        let resultadoEuclides = AlgoritmoExtendidoEuclides(denominadorPositivo,n);
                        let inversoDenominador = resultadoEuclides.inverso;
                        procedimientoHTML += resultadoEuclides.tabla;
                        // Resultado de lambda
                        let valorlambda = numeradorPositivo*inversoDenominador;
                        let valorlambdaPositivo;
                        // Si lambda es negativo, entonces utiliza el inverso aditivo
                        if(valorlambda<0){
                            valorlambdaPositivo = n - (Math.abs(valorlambda)%n);
                        }else{
                            valorlambdaPositivo = valorlambda%n;
                        }
                        // Continuación de la operación Lambda debajo de la tabla
                        procedimientoHTML += `<div class="lambda-continuation" id="continuacionLambda"><b>λ =</b> (${numeradorPositivo}) * (${denominadorPositivo})<sup>-1</sup> = (${numeradorPositivo})*(${inversoDenominador}) mod ${n} = <b>${valorlambdaPositivo}</b></div>`;
                        // Se calcula x3
                        let x3 = (valorlambdaPositivo * valorlambdaPositivo - 2*x1Temp);
                        
                        // Realiza el inverso aditivo en caso de que x3 sea negativo
                        if(x3<0){
                            x3Positivo = n - (Math.abs(x3)%n);
                        }else{
                            x3Positivo = x3%n;
                        }
                        procedimientoHTML += `<div class="calculation-result" id="valorx3"><b>x<sub>3</sub></b> = [(λ)<sup>2</sup> - 2*x<sub>1</sub>] mod p = [(${valorlambdaPositivo})<sup>2</sup> - 2*${x1Temp}] mod ${n} = <b>${x3Positivo}</b></div>`;
                        // Se calcula y3
                        let y3 = (valorlambdaPositivo*(x1Temp - x3Positivo)-y1Temp);
                        
                        // Realiza el inverso aditivo en caso de que y3 sea negativo
                        if(y3<0){
                            y3Positivo = n - (Math.abs(y3)%n);
                        }else{
                            y3Positivo = y3%n;
                        }
                        procedimientoHTML += `<div class="calculation-result" id="valory3"><b>y<sub>3</sub></b> = (λ * (x<sub>1</sub> - x<sub>3</sub>) - y<sub>1</sub>) mod p = ((${valorlambdaPositivo}) * ((${x1Temp}) - (${x3Positivo})) - (${y1Temp})) mod ${n} = <b>${y3Positivo}</b></div>`;
                        procedimientoHTML +=  `<div class="result-box" id="resultadoAlgoritmoEuclides"><b>P(${x3Positivo},${y3Positivo})</b></div>`;

                        x1 = x3Positivo;
                        y1 = y3Positivo;

                    }
                } 
            }
            document.getElementById("contenedorDoblado").innerHTML = procedimientoHTML;
            return [x3Positivo,y3Positivo];
        }


        function CalcularSumaPuntos(n,x1,y1,potencia){
        n = Number(n);
        //x1 = Number(x1);
        //y1 = Number(y1);
        //x2 = Number(x2);
        //y2 = Number(y2);
        //potencia1 = Number(potencia1);
        //potencia2 = Number(potencia2);
        //potencia1 = 2**potencia1;
        //potencia2 = 2**potencia2;
        //contadorSumas = Number(contadorSumas);
        //contadorDoblados = Number(contadorDoblados);
        //contadorDoblados = 2**contadorDoblados;
        let sumaPuntos = 0;
        let procedimientoHTML2 = "";
        for (let i = 0; i < (x1.length-1); i++) {
            potencia[i] = Number(potencia[i]);
            potencia[i+1] = Number(potencia[i+1]);
            if(i==0){
                potencia1 = 2**potencia[i];
                potencia2 = 2**potencia[i+1];
                potencia3 = potencia1+potencia2;
                procedimientoHTML2 += `<div class="final-point" id="valorFinalPunto1"><b>${potencia1}P + ${potencia2}P = ${potencia3}P</b></div>`;
            }else{
                potencia2 = 2**potencia[i+1];
                potencia4 = potencia3+(potencia2);
                procedimientoHTML2 += `<div class="final-point" id="valorFinalPunto1"><b>${potencia3}P + ${potencia2}P = ${potencia4}P</b></div>`;
                potencia3 = potencia3+2**potencia[i+1];
            }
            //let valorIteracion = (contadorDoblados + 1)+i;
            
            // Obtiene los valores de las casillas

            // Se calcula el inverso aditivo
            let x1Temp;
            let x2Temp;
            let y1Temp;
            let y2Temp;
            // Se calcula el inverso aditivo por si hay un valor negativo
            if(x1[i]<0){
                x1[i] = Math.abs(x1[i]);
                x1Temp = n - (x1[i]%n);
            }else{
                x1Temp = x1[i];
            }
            if(x1[i+1]<0){
                x1[i+1] = Math.abs(x1[i+1]);
                x2Temp = n - (x1[i+1]%n);
            }else{
                x2Temp = x1[i+1];
            }
            if(y1[i]<0){
                y1[i] = Math.abs(y1[i]);
                y1Temp = n - (y1[i]%n);
            }else{
                y1Temp = y1[i];
            }
            if(y1[i+1]<0){
                y1[i+1] = Math.abs(y1[i+1]);
                y2Temp = n - (y1[i+1]%n);
            }else{
                y2Temp = y1[i+1];
            }
            // Error si n es menor o igual a 0
            if(n<=0){
                //let error = document.getElementById("mensajeError1");
                //error.innerHTML = "El valor de n no puede ser menor o igual a cero";
                //error.style.display = "block";
                //operaciones.style.display = "none";
            }else{
                //error.style.display = "none";
                //operaciones.style.display = "none";
                // Calcula el numerador y el denominador 
                let numerador = y2Temp - y1Temp;
                let denominador = x2Temp - x1Temp;
                let numeradorPositivo;
                let denominadorPositivo;
                numeradorPositivo = numerador;       
                // Se calcula el inverso aditivo si el denominador es menor a cero
                if(denominador<0){
                    denominador = Math.abs(denominador);
                    denominadorPositivo = n - (denominador%n);
                }else if(denominador==0){
                    procedimientoHTML2 += `<div class="alert alert-danger" role="alert" id="mensajeError1">El valor tiende a infinito</div>`;
                    //break;
                }else{
                    denominadorPositivo = denominador;
                }
                // Error si el numerador es 0
                if(denominador == 0){
                    error.innerHTML = "El numerador es cero";
                    error.style.display = "block";
                }else{
                    operaciones.style.display = "block";
                    // Texto inicial de lambda
                    procedimientoHTML2 += `<div class="lambda-box" id="lambda1"><b>λ</b> = (y<sub>2</sub> - y<sub>1</sub>)/(x<sub>2</sub> - x<sub>1</sub>) = (${y2Temp} - ${y1Temp})/(${x2Temp} - ${x1Temp}) = (${numeradorPositivo})/(${denominadorPositivo}) = (${numeradorPositivo}) * (${denominadorPositivo})<sup>-1</sup></div>`;
                    // Tabla del algoritmo extendido de Euclides
                    procedimientoHTML2 += `<h4 class="procedure-subtitle" id="tituloTablas1"><b>Algoritmo extendido de Euclides</b></h4>`;
                    // Se realiza el algoritmo extendido de Euclides
                    let resultadoEuclides = AlgoritmoExtendidoEuclides(denominadorPositivo,n);
                    let inversoDenominador = resultadoEuclides.inverso;
                    procedimientoHTML2 += resultadoEuclides.tabla;
                    // Resultado de lambda
                    let valorlambda = numeradorPositivo*inversoDenominador;
                    let valorlambdaPositivo;
                    // Si lambda es negativo, entonces utiliza el inverso aditivo
                    if(valorlambda<0){
                        valorlambdaPositivo = n - (Math.abs(valorlambda)%n);
                    }else{
                        valorlambdaPositivo = valorlambda%n;
                    }
                    // Continuación de la operación Lambda debajo de la tabla
                    procedimientoHTML2 += `<div class="lambda-continuation" id="continuacionLambda1"><b>λ =</b> (${numeradorPositivo}) * (${denominadorPositivo})<sup>-1</sup> = (${numeradorPositivo}) * (${inversoDenominador}) mod ${n} = <b>${valorlambdaPositivo}</b></div>`;
                    // Se calcula x3
                    let x3 = (valorlambdaPositivo * valorlambdaPositivo - x1Temp - x2Temp);
                    let x3Positivo;
                    // Realiza el inverso aditivo en caso de que x3 sea negativo
                    if(x3<0){
                        x3Positivo = n - (Math.abs(x3)%n);
                    }else{
                        x3Positivo = x3%n;
                    }
                    procedimientoHTML2 += `<div class="calculation-result" id="valorx31"><b>x<sub>3</sub></b> = ((λ)<sup>2</sup> - x<sub>1</sub> - x<sub>2</sub>) mod p = ((${valorlambdaPositivo})<sup>2</sup> - (${x1Temp}) - (${x2Temp})) mod ${n} = <b>${x3Positivo}</b></div>`;
                    // Se calcula y3
                    let y3 = (valorlambdaPositivo*(x1Temp - x3Positivo)-y1Temp);
                    let y3Positivo;
                    // Realiza el inverso aditivo en caso de que y3 sea negativo
                    if(y3<0){
                        y3Positivo = n - (Math.abs(y3)%n);
                    }else{
                        y3Positivo = y3%n;
                    }
                    procedimientoHTML2 += `<div class="calculation-result" id="valory31"><b>y<sub>3</sub></b> = (λ * (x<sub>1</sub> - x<sub>3</sub>) - y<sub>1</sub>) mod p = ((${valorlambdaPositivo}) * ((${x1Temp}) - (${x3Positivo})) - (${y1Temp})) mod ${n} = <b>${y3Positivo}</b></div>`;
                    procedimientoHTML2 +=  `<div class="result-box" id="resultadoAlgoritmoEuclides1"><b>P(${x3Positivo},${y3Positivo})</b></div>`;
                    x1[1] = x3Positivo;
                    y1[1] = y3Positivo;


                    console.log("x1: "+x1);
                    console.log("y1: "+y1);
                    //x2 = x3Positivo;
                    //y2 = y3Positivo;
                }
            } 
        }
        document.getElementById("contenedorSuma").innerHTML = procedimientoHTML2;
        
    }



            // Función Algoritmo Extendido de Euclides donde recibe el denominador y n
            function AlgoritmoExtendidoEuclides(a,n){
                let s = [1,0];
                let t = [0,1];
                let r = [n,a];
                let q = [];
                let divisor = a;
                let dividendo = n;
                let contador = 0;
                let resultado = 0;
                let moduloTemp = 0;
                procedimientoHTML1 = '<table class="table table-hover" id="tablaDatos">';
                while(r[contador+1] != 1){
                    // Se redondea el cociente
                    q.push(Math.floor(r[contador]/r[contador+1]))   
                    // Se calcula el residuo
                    r.push(r[contador]%r[contador+1])   
                    //r.push(moduloTemp);
                    s.push(s[contador] - q[contador]*s[contador+1]);
                    t.push(t[contador] - q[contador]*t[contador+1]);
                    contador = contador + 1;
                }
                
                // Mostrar valores en la tabla
                //let tabla = document.getElementById("tablaDatos");
                //tabla.innerHTML = "";
                // Busca el arreglo con el mayor número de datos
                let max = Math.max(q.length,r.length,s.length,t.length);
                // Tabla con los datos del algoritmo extendido de Euclides
                procedimientoHTML1 += '<thead><tr><th scope="col">q</th><th scope="col">r</th><th scope="col">s</th><th scope="col">t</th></tr></thead>';
                // Agrega los datos a la tabla
                for(let i = 0; i < max; i++){
                    let qTemp = q[i] || "";
                    let rTemp = r[i] || "";
                    let sTemp = s[i] || "";
                    let tTemp = t[i] || "";
                    procedimientoHTML1 += 
                    "<tr>"+
                        "<td>"+qTemp+"</td>"+
                        "<td>"+rTemp+"</td>"+
                        "<td>"+sTemp+"</td>"+
                        "<td>"+tTemp+"</td>"+
                    "</tr>";
                }
                procedimientoHTML1+='</table>';
                // Imprime el resultado
                procedimientoHTML1+= `<div class="result-box" id="resultadoAlgoritmoEuclides">${r[contador+1]} = (${s[contador+1]}) * (${n}) + (${t[contador+1]}) * (${a})</div>`;
                //document.getElementById("resultadoAlgoritmoEuclides").innerHTML=r[contador+1]+" = ("+s[contador+1] +") * ("+n+") + ("+t[contador+1]+") * ("+a+")";
                if(t[contador+1]<0){
                    t[contador+1] = Math.abs(t[contador+1]);
                    resultado = n - (t[contador+1]%n);
                }else{
                    resultado = t[contador+1]
                }
                //document.getElementById("contenedorDoblado").innerHTML = procedimientoHTML1;
                return{
                    inverso: resultado,
                    tabla: procedimientoHTML1
                };
            }


        } 