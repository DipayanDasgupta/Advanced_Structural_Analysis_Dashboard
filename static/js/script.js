// static/js/script.js
document.addEventListener('DOMContentLoaded', function () {
    // --- DOM Element References ---
    const elementTypeSelect = document.getElementById('elementTypeSelect');
    const commonPropsFieldset = document.getElementById('commonProps');
    const crossSectionPropsFieldset = document.getElementById('crossSectionProps');
    const beamInputsFieldset = document.getElementById('beamInputs');
    const columnInputsFieldset = document.getElementById('columnInputs');

    const lengthInput = document.getElementById('length');
    const lengthValueDisplay = document.getElementById('lengthValue');
    const materialSelect = document.getElementById('materialSelect');

    const sectionTypeSelect = document.getElementById('sectionTypeSelect');
    const rectangularParamsDiv = document.getElementById('rectangularParams');
    const rectWidthInput = document.getElementById('rectWidth');
    const rectWidthValueDisplay = document.getElementById('rectWidthValue');
    const rectHeightInput = document.getElementById('rectHeight');
    const rectHeightValueDisplay = document.getElementById('rectHeightValue');
    const circularParamsDiv = document.getElementById('circularParams');
    const circDiameterInput = document.getElementById('circDiameter');
    const circDiameterValueDisplay = document.getElementById('circDiameterValue');

    const beamSupportTypeSelect = document.getElementById('beamSupportType');
    const beamLoadTypeSelect = document.getElementById('beamLoadType');
    const beamPointLoadInputsDiv = document.getElementById('beamPointLoadInputs');
    const pointLoadInput = document.getElementById('pointLoad');
    const pointLoadValueDisplay = document.getElementById('pointLoadValue');
    const pointLoadPositionContainer = document.getElementById('pointLoadPositionContainer');
    const pointLoadPositionRatioInput = document.getElementById('pointLoadPositionRatio');
    const pointLoadPositionRatioValueDisplay = document.getElementById('pointLoadPositionRatioValue');
    const beamUdlInputsDiv = document.getElementById('beamUdlInputs');
    const udlValueInput = document.getElementById('udlValue');
    const udlValueDisplay = document.getElementById('udlValueDisplay');

    const axialLoadInput = document.getElementById('axialLoad');
    const axialLoadValueDisplay = document.getElementById('axialLoadValue');
    const columnEndConditionSelect = document.getElementById('columnEndConditionSelect');
    const effLengthFactorKxContainer = document.getElementById('effLengthFactorKxContainer');
    const effLengthFactorKyContainer = document.getElementById('effLengthFactorKyContainer');
    const effLengthFactorKxInput = document.getElementById('effLengthFactorKx');
    const effLengthFactorKxValueDisplay = document.getElementById('effLengthFactorKxValue');
    const effLengthFactorKyInput = document.getElementById('effLengthFactorKy');
    const effLengthFactorKyValueDisplay = document.getElementById('effLengthFactorKyValue');

    const calculateButton = document.getElementById('calculateButton');
    const errorDisplay = document.getElementById('errorDisplay');
    const summaryResultsDiv = document.getElementById('summaryResults');
    const failureChecksListDiv = document.getElementById('failureChecksList');
    const jsonOutputPre = document.getElementById('jsonOutput');

    const beamPlotsDiv = document.getElementById('beamPlots');
    const columnPlotsDiv = document.getElementById('columnPlots');
    const sfdPlotDiv = document.getElementById('sfdPlot');
    const bmdPlotDiv = document.getElementById('bmdPlot');
    const deflectionPlotDiv = document.getElementById('deflectionPlot');

    const elementDiagramCanvas = document.getElementById('elementDiagramCanvas');
    const elementCtx = elementDiagramCanvas.getContext('2d');
    const crossSectionCanvas = document.getElementById('crossSectionCanvas');
    const csCtx = crossSectionCanvas.getContext('2d');
    const crossSectionStressInfoDiv = document.getElementById('crossSectionStressInfo');

    const placeholderTexts = document.querySelectorAll('.placeholder-text');
    const elementDiagramPlaceholder = document.getElementById('elementDiagramPlaceholder');
    const csCanvasPlaceholder = document.getElementById('csCanvasPlaceholder');
    const jsonOutputPlaceholder = document.getElementById('jsonOutputPlaceholder');


    // --- Theme Colors & Theme Management ---
    let themeColors = {}; // Will be populated by fetchThemeColors

    function fetchThemeColors() {
        const rootStyle = getComputedStyle(document.documentElement);
        themeColors = {
            primary: rootStyle.getPropertyValue('--primary-color').trim(),
            primaryHover: rootStyle.getPropertyValue('--primary-hover-color').trim(),
            text: rootStyle.getPropertyValue('--text-color').trim(),
            textLight: rootStyle.getPropertyValue('--text-color-light').trim(),
            mutedText: rootStyle.getPropertyValue('--muted-text-color').trim(),
            border: rootStyle.getPropertyValue('--border-color').trim(),
            cardBackground: rootStyle.getPropertyValue('--card-background-color').trim(),
            danger: rootStyle.getPropertyValue('--danger-color').trim(),
            success: rootStyle.getPropertyValue('--success-color').trim(),
            fontFamily: rootStyle.getPropertyValue('--font-family').trim(),
            diagramSupportColor: rootStyle.getPropertyValue('--diagram-support-color').trim(),
            diagramLoadColor: rootStyle.getPropertyValue('--diagram-load-color').trim(),
            diagramUdlColor: rootStyle.getPropertyValue('--diagram-udl-color').trim(),
            diagramDeflectedShapeColor: rootStyle.getPropertyValue('--diagram-deflected-shape-color').trim(),
            diagramBuckledShapeColor: rootStyle.getPropertyValue('--diagram-buckled-shape-color').trim(),
            diagramDimensionLineColor: rootStyle.getPropertyValue('--diagram-dimension-line-color').trim(),
            diagramNeutralAxisColor: rootStyle.getPropertyValue('--diagram-neutral-axis-color').trim(),
            diagramGridLineColor: rootStyle.getPropertyValue('--diagram-grid-line-color').trim(),
            diagramTextColor: rootStyle.getPropertyValue('--diagram-text-color').trim(),
            stressTensionMax: rootStyle.getPropertyValue('--stress-tension-color-max').trim(),
            stressCompressionMax: rootStyle.getPropertyValue('--stress-compression-color-max').trim(),
            stressNeutral: rootStyle.getPropertyValue('--stress-neutral-color').trim(),
        };
    }

    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeIconLight = document.getElementById('themeIconLight');
    const themeIconDark = document.getElementById('themeIconDark');
    const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
    let currentResultsData = null; // Store last successful calculation data
    let currentInputPayloadData = null; // Store last input payload

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        fetchThemeColors(); // Update JS color object

        if (theme === 'dark') {
            themeIconLight.style.display = 'none';
            themeIconDark.style.display = 'inline-block';
        } else {
            themeIconLight.style.display = 'inline-block';
            themeIconDark.style.display = 'none';
        }

        // Re-render Plotly charts and Canvas diagrams if data exists
        if (currentResultsData && currentInputPayloadData) {
            displayResults(currentResultsData, currentInputPayloadData, false); // false to prevent clearing inputs
        } else {
            // If no results yet, just ensure canvas placeholders are correctly styled if needed
            // (though they should adapt via CSS vars for color)
            // Also, clear any lingering canvas drawings if theme changes before first calc
            clearDiagramsOnly();
        }
    }
    
    function clearDiagramsOnly() {
        if (sfdPlotDiv && typeof Plotly !== 'undefined' && sfdPlotDiv.data) Plotly.purge(sfdPlotDiv);
        if (bmdPlotDiv && typeof Plotly !== 'undefined' && bmdPlotDiv.data) Plotly.purge(bmdPlotDiv);
        if (deflectionPlotDiv && typeof Plotly !== 'undefined' && deflectionPlotDiv.data) Plotly.purge(deflectionPlotDiv);
        if (elementCtx) elementCtx.clearRect(0, 0, elementDiagramCanvas.width, elementDiagramCanvas.height);
        if (csCtx) csCtx.clearRect(0, 0, crossSectionCanvas.width, crossSectionCanvas.height);
        if(elementDiagramPlaceholder) elementDiagramPlaceholder.style.display = 'block';
        if(csCanvasPlaceholder) csCanvasPlaceholder.style.display = 'block';
    }


    // Get theme from local storage or system preference
    const savedTheme = localStorage.getItem('theme');
    const initialTheme = savedTheme || (prefersDarkScheme.matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', initialTheme); // Set initial theme on HTML element
    fetchThemeColors(); // Fetch colors based on initial theme
    setTheme(initialTheme); // Then call setTheme to apply icons etc.


    themeToggleBtn.addEventListener('click', () => {
        const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });
    prefersDarkScheme.addEventListener('change', (e) => {
        setTheme(e.matches ? 'dark' : 'light');
    });


    // --- Event Listeners for UI Updates ---
    function updateValueDisplay(inputElem, displayElem, unit = '', multiplier = 1, fixed = 2) {
        if (inputElem && displayElem) {
            let value = parseFloat(inputElem.value) * multiplier;
            if (isNaN(value)) value = 0;
            displayElem.textContent = `${value.toFixed(fixed)} ${unit}`;
        }
    }

    lengthInput.addEventListener('input', () => updateValueDisplay(lengthInput, lengthValueDisplay, 'm'));
    rectWidthInput.addEventListener('input', () => updateValueDisplay(rectWidthInput, rectWidthValueDisplay, 'mm'));
    rectHeightInput.addEventListener('input', () => updateValueDisplay(rectHeightInput, rectHeightValueDisplay, 'mm'));
    circDiameterInput.addEventListener('input', () => updateValueDisplay(circDiameterInput, circDiameterValueDisplay, 'mm'));
    pointLoadInput.addEventListener('input', () => updateValueDisplay(pointLoadInput, pointLoadValueDisplay, 'kN'));
    if(udlValueInput) udlValueInput.addEventListener('input', () => updateValueDisplay(udlValueInput, udlValueDisplay, 'kN/m'));

    pointLoadPositionRatioInput.addEventListener('input', () => {
        const ratio = parseFloat(pointLoadPositionRatioInput.value);
        let text = `${ratio.toFixed(2)}`;
        if (Math.abs(ratio - 0.5) < 0.01) text += ' (Mid-span)';
        else if (ratio <= 0.05) text += ' (Near Left)';
        else if (ratio >= 0.95) text += ' (Near Right)';
        pointLoadPositionRatioValueDisplay.textContent = text;
    });
    axialLoadInput.addEventListener('input', () => updateValueDisplay(axialLoadInput, axialLoadValueDisplay, 'kN'));
    effLengthFactorKxInput.addEventListener('input', () => updateValueDisplay(effLengthFactorKxInput, effLengthFactorKxValueDisplay, '', 1, 2));
    effLengthFactorKyInput.addEventListener('input', () => updateValueDisplay(effLengthFactorKyInput, effLengthFactorKyValueDisplay, '', 1, 2));

    if(columnEndConditionSelect) {
        columnEndConditionSelect.addEventListener('change', function() {
            const selectedValue = this.value;
            const isCustom = selectedValue === 'custom';
            effLengthFactorKxInput.readOnly = !isCustom;
            effLengthFactorKyInput.readOnly = !isCustom;
            effLengthFactorKxInput.disabled = !isCustom;
            effLengthFactorKyInput.disabled = !isCustom;
            effLengthFactorKxContainer.style.opacity = isCustom ? '1' : '0.65';
            effLengthFactorKyContainer.style.opacity = isCustom ? '1' : '0.65';
            if (!isCustom) {
                const [kx, ky] = selectedValue.split(',').map(v => parseFloat(v));
                effLengthFactorKxInput.value = kx.toFixed(2);
                effLengthFactorKyInput.value = ky.toFixed(2);
                effLengthFactorKxInput.dispatchEvent(new Event('input'));
                effLengthFactorKyInput.dispatchEvent(new Event('input'));
            }
        });
    }

    elementTypeSelect.addEventListener('change', toggleElementInputs);
    sectionTypeSelect.addEventListener('change', toggleSectionParams);
    beamSupportTypeSelect.addEventListener('change', filterBeamLoadTypes);
    beamLoadTypeSelect.addEventListener('change', toggleBeamLoadInputs);

    function toggleElementInputs() {
        const type = elementTypeSelect.value;
        const isBeam = type === 'beam';
        beamInputsFieldset.style.display = isBeam ? 'block' : 'none';
        columnInputsFieldset.style.display = !isBeam ? 'block' : 'none';
        beamPlotsDiv.style.display = isBeam ? 'block' : 'none';
        columnPlotsDiv.style.display = !isBeam ? 'block' : 'none';
        if (isBeam) filterBeamLoadTypes();
        else if(columnEndConditionSelect) columnEndConditionSelect.dispatchEvent(new Event('change'));
    }

    function toggleSectionParams() {
        const type = sectionTypeSelect.value;
        rectangularParamsDiv.style.display = (type === 'rectangular') ? 'block' : 'none';
        circularParamsDiv.style.display = (type === 'circular') ? 'block' : 'none';
    }

    function filterBeamLoadTypes() {
        if (elementTypeSelect.value !== 'beam') return;
        const supportType = beamSupportTypeSelect.value;
        let firstVisibleOption = null;
        let currentSelectedValue = beamLoadTypeSelect.value;
        let currentSelectedStillVisible = false;
        for (let option of beamLoadTypeSelect.options) {
            const isSupported = option.dataset.support === supportType || !option.dataset.support;
            option.style.display = isSupported ? '' : 'none';
            if (isSupported) {
                if (!firstVisibleOption) firstVisibleOption = option;
                if (option.value === currentSelectedValue) currentSelectedStillVisible = true;
            }
        }
        if (!currentSelectedStillVisible && firstVisibleOption) beamLoadTypeSelect.value = firstVisibleOption.value;
        else if (!currentSelectedStillVisible && !firstVisibleOption) beamLoadTypeSelect.value = "";
        toggleBeamLoadInputs();
    }

    function toggleBeamLoadInputs() {
        if (elementTypeSelect.value !== 'beam') return;
        const loadType = beamLoadTypeSelect.value;
        beamPointLoadInputsDiv.style.display = 'none';
        pointLoadPositionContainer.style.display = 'none';
        if(beamUdlInputsDiv) beamUdlInputsDiv.style.display = 'none';

        if (loadType === 'pointLoad') {
            beamPointLoadInputsDiv.style.display = 'block';
            pointLoadPositionContainer.style.display = 'flex';
        } else if (loadType === 'pointLoadEnd') {
            beamPointLoadInputsDiv.style.display = 'block';
        } else if (loadType === 'udl') {
            if(beamUdlInputsDiv) beamUdlInputsDiv.style.display = 'block';
        }
    }

    calculateButton.addEventListener('click', performCalculation);

    async function performCalculation() {
        errorDisplay.style.display = 'none'; errorDisplay.textContent = '';
        placeholderTexts.forEach(el => el.style.display = 'none'); // Hide all placeholders

        calculateButton.disabled = true;
        calculateButton.innerHTML = '<span class="spinner"></span> Calculating...';

        const payload = { /* ... (same as before) ... */
            elementType: elementTypeSelect.value,
            length: parseFloat(lengthInput.value),
            material: materialSelect.value,
            sectionType: sectionTypeSelect.value,
            sectionParams: [],
        };
        if (payload.sectionType === 'rectangular') payload.sectionParams = [parseFloat(rectWidthInput.value), parseFloat(rectHeightInput.value)];
        else if (payload.sectionType === 'circular') payload.sectionParams = [parseFloat(circDiameterInput.value)];

        if (payload.elementType === 'beam') {
            payload.beamSupportType = beamSupportTypeSelect.value;
            payload.beamLoadType = beamLoadTypeSelect.value;
            if (payload.beamLoadType === 'pointLoad' || payload.beamLoadType === 'pointLoadEnd') {
                payload.pointLoad = parseFloat(pointLoadInput.value);
                if (payload.beamLoadType === 'pointLoad') payload.pointLoadPositionRatio = parseFloat(pointLoadPositionRatioInput.value);
            } else if (payload.beamLoadType === 'udl') payload.udlValue = parseFloat(udlValueInput.value);
        } else if (payload.elementType === 'column') {
            payload.axialLoad = parseFloat(axialLoadInput.value);
            payload.effLengthFactorKx = parseFloat(effLengthFactorKxInput.value);
            payload.effLengthFactorKy = parseFloat(effLengthFactorKyInput.value);
        }

        try {
            const response = await fetch('/calculate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            const data = await response.json();
            if (!response.ok || data.error) throw new Error(data.error || `Server error: ${response.status}`);
            
            currentResultsData = data; // Store for theme changes
            currentInputPayloadData = payload; // Store for theme changes
            displayResults(data, payload, true); // true to clear previous results fully

        } catch (err) {
            console.error("Calculation error:", err);
            errorDisplay.textContent = `Error: ${err.message}`;
            errorDisplay.style.display = 'block';
            clearResults(false); // Clear results but keep inputs
            currentResultsData = null; currentInputPayloadData = null; // Clear stored data on error
        } finally {
            calculateButton.disabled = false;
            calculateButton.textContent = 'Calculate & Visualize';
        }
    }

    function clearResults(fullClear = true) {
        summaryResultsDiv.innerHTML = '';
        failureChecksListDiv.innerHTML = '';
        jsonOutputPre.textContent = '';
        
        clearDiagramsOnly(); // Clears plots and canvas, shows placeholders

        if (fullClear) {
            // Optionally clear input fields if needed, but generally not desired on new calc
             placeholderTexts.forEach(el => el.style.display = 'block'); // Show all placeholders on full clear
        } else {
            // If not full clear (e.g. error occurred), specific placeholders for results area can be shown
            if (summaryResultsDiv.innerHTML === '') summaryResultsDiv.innerHTML = `<p class="placeholder-text" style="text-align: center; color: var(--muted-text-color);">Calculation failed or no results.</p>`;
            if (failureChecksListDiv.innerHTML === '') failureChecksListDiv.innerHTML = `<p class="placeholder-text" style="text-align: center; color: var(--muted-text-color);">No failure checks to display.</p>`;
        }
    }
    
    // Helper function for Title Case in JavaScript
    function toTitleCase(str) {
        if (!str || typeof str !== 'string') return '';
        return str.replace(/_/g, ' ').toLowerCase().split(' ')
                  .map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }

    function displayResults(data, inputPayload, isNewCalculation = true) {
        if (isNewCalculation) clearResults(true); // Full clear for a new calculation
        else clearDiagramsOnly(); // Only clear diagrams if re-rendering for theme change

        placeholderTexts.forEach(el => el.style.display = 'none');
        if(elementDiagramPlaceholder) elementDiagramPlaceholder.style.display = 'none';
        if(csCanvasPlaceholder) csCanvasPlaceholder.style.display = 'none';
        if(jsonOutputPlaceholder) jsonOutputPlaceholder.style.display = 'none';


        const { element_info, results } = data;
        jsonOutputPre.textContent = JSON.stringify(data, null, 2);

        let summaryHtml = `<h4>Element: ${inputPayload.elementType.toUpperCase()}</h4>`;
        summaryHtml += `<p><strong>Length:</strong> ${element_info.length_m.toFixed(2)} m</p>`;
        summaryHtml += `<p><strong>Material:</strong> ${toTitleCase(element_info.material.name)}</p>`;
        summaryHtml += `<p><strong>Cross-section:</strong> ${toTitleCase(element_info.cross_section.type)} (Area: ${(element_info.cross_section.area_m2 * 1e6).toFixed(1)} mm²)</p>`;

        if (inputPayload.elementType === 'beam') {
            summaryHtml += `<p><strong>Max Shear (abs):</strong> ${Math.max(Math.abs(results.max_shear_N || 0), Math.abs(results.min_shear_N || 0)).toFixed(1)} N</p>`;
            summaryHtml += `<p><strong>Max Moment (abs):</strong> ${Math.max(Math.abs(results.max_moment_Nm || 0), Math.abs(results.min_moment_Nm || 0)).toFixed(1)} Nm</p>`;
            summaryHtml += `<p><strong>Max Deflection (abs):</strong> ${(Math.max(Math.abs(results.max_deflection_m || 0), Math.abs(results.min_deflection_m || 0)) * 1000).toFixed(2)} mm</p>`;
            summaryHtml += `<p><strong>Max Bending Stress (abs):</strong> ${(Math.max(Math.abs(results.max_bending_stress_Pa || 0), Math.abs(results.min_bending_stress_Pa || 0))/1e6).toFixed(2)} MPa</p>`;
            summaryHtml += `<p><strong>Max Shear Stress (approx):</strong> ${((results.max_shear_stress_Pa || 0)/1e6).toFixed(2)} MPa</p>`;

            const x_sfd = results.sfd_points.map(p => p.x); const v_sfd = results.sfd_points.map(p => p.v / 1000);
            const x_bmd = results.bmd_points.map(p => p.x); const m_bmd = results.bmd_points.map(p => p.m / 1000);
            const x_defl = results.deflection_points.map(p => p.x); const d_defl = results.deflection_points.map(p => p.d * 1000);

            plotDiagram(sfdPlotDiv, x_sfd, v_sfd, 'Position (m)', 'Shear Force (kN)', 'Shear Force Diagram (SFD)');
            plotDiagram(bmdPlotDiv, x_bmd, m_bmd, 'Position (m)', 'Bending Moment (kNm)', 'Bending Moment Diagram (BMD)', true);
            plotDiagram(deflectionPlotDiv, x_defl, d_defl, 'Position (m)', 'Deflection (mm)', 'Deflection Diagram', results.max_deflection_m < 0);
            drawBeamDiagram(element_info, results, inputPayload);
            drawCrossSectionStress(element_info, results, inputPayload.elementType);
        } else if (inputPayload.elementType === 'column') {
            summaryHtml += `<p><strong>Axial Load (P):</strong> ${(inputPayload.axialLoad).toFixed(1)} kN</p>`;
            summaryHtml += `<p><strong>Axial Stress (σ):</strong> ${((results.axial_stress_Pa || 0) / 1e6).toFixed(2)} MPa</p>`;
            summaryHtml += `<p><strong>Min Critical Buckling Load (Pcr):</strong> ${((results.min_critical_buckling_load_N || 0) / 1000).toFixed(1)} kN</p>`;
            summaryHtml += `<p style="padding-left: 15px;">• Pcr,x: ${((results.critical_buckling_load_Pcr_x_N || 0) / 1000).toFixed(1)} kN (Kx=${element_info.Kx !== undefined ? element_info.Kx.toFixed(2) : 'N/A'})</p>`;
            summaryHtml += `<p style="padding-left: 15px;">• Pcr,y: ${((results.critical_buckling_load_Pcr_y_N || 0) / 1000).toFixed(1)} kN (Ky=${element_info.Ky !== undefined ? element_info.Ky.toFixed(2) : 'N/A'})</p>`;
            drawColumnDiagram(element_info, results, inputPayload);
            drawCrossSectionStress(element_info, results, inputPayload.elementType);
        }
        summaryResultsDiv.innerHTML = summaryHtml;

        let failureHtml = '<ul>';
        if (results.failure_checks && Object.keys(results.failure_checks).length > 0) {
            for (const key in results.failure_checks) {
                const check = results.failure_checks[key];
                const statusClass = check.status.startsWith("PASS") ? "status-pass" : "status-fail";
                const checkTitle = toTitleCase(key);
                failureHtml += `<li><strong>${checkTitle}:</strong> <span class="status ${statusClass}">${check.status.toUpperCase()}</span> <span class="details">`;
                if (typeof check.ratio === 'number') failureHtml += `Ratio: ${check.ratio.toFixed(3)}`; else failureHtml += `Ratio: ${check.ratio}`;
                if (check.demand_Pa !== undefined) failureHtml += ` <br>Demand: ${(check.demand_Pa/1e6).toFixed(2)} MPa`;
                if (check.capacity_Pa !== undefined) failureHtml += ` | Capacity: ${(check.capacity_Pa/1e6).toFixed(2)} MPa`;
                if (check.demand_N !== undefined) failureHtml += ` <br>Demand: ${(check.demand_N/1000).toFixed(1)} kN`;
                if (check.capacity_N !== undefined) failureHtml += ` | Capacity: ${(check.capacity_N/1000).toFixed(1)} kN`;
                if (check.demand_m !== undefined) failureHtml += ` <br>Demand: ${(check.demand_m*1000).toFixed(2)} mm`;
                if (check.limit_m !== undefined) failureHtml += ` | Limit${check.limit_description ? ` (${check.limit_description})` : ''}: ${(check.limit_m*1000).toFixed(2)} mm`;
                failureHtml += `</span>`;
                if (check.note) failureHtml += `<small class="status-note">${check.note}</small>`;
                failureHtml += `</li>`;
            }
        } else failureHtml += `<li><p class="placeholder-text" style="text-align: center; color: var(--muted-text-color);">No failure checks performed or available.</p></li>`;
        failureHtml += '</ul>';
        failureChecksListDiv.innerHTML = failureHtml;
    }

    function plotDiagram(divElement, xData, yData, xAxisTitle, yAxisTitle, plotTitle, invertY = false) {
        const trace = {
            x: xData, y: yData, type: 'scatter', mode: 'lines+markers',
            marker: { size: 6, color: themeColors.primaryHover || '#0056b3' },
            line: { color: themeColors.primary || '#007bff', width: 2.5 }
        };
        const layout = {
            title: { text: plotTitle, font: { family: themeColors.fontFamily, size: 18, color: themeColors.text }, x: 0.05, xanchor: 'left', y: 0.95, yanchor: 'top'},
            xaxis: { title: { text: xAxisTitle, font: { family: themeColors.fontFamily, size: 14, color: themeColors.mutedText } }, zeroline: true, zerolinewidth:1.5, zerolinecolor: themeColors.diagramGridLineColor, gridcolor: themeColors.diagramGridLineColor, tickfont: { family: themeColors.fontFamily, color: themeColors.textLight }, linecolor: themeColors.border, mirror: true },
            yaxis: { title: { text: yAxisTitle, font: { family: themeColors.fontFamily, size: 14, color: themeColors.mutedText } }, zeroline: true, zerolinewidth:1.5, zerolinecolor: themeColors.diagramGridLineColor, autorange: invertY ? 'reversed' : true, gridcolor: themeColors.diagramGridLineColor, tickfont: { family: themeColors.fontFamily, color: themeColors.textLight }, linecolor: themeColors.border, mirror: true },
            margin: { l: 75, r: 30, t: 70, b: 65 },
            paper_bgcolor: themeColors.cardBackground,
            plot_bgcolor: themeColors.cardBackground,
            font: { family: themeColors.fontFamily, color: themeColors.text }
        };
        Plotly.newPlot(divElement, [trace], layout, {responsive: true, displaylogo: false});
    }

    // --- Canvas Drawing Functions ---
    // (Make sure these functions use the themeColors object for all color assignments)
    function drawBeamDiagram(element_info, results, inputs) {
        elementCtx.clearRect(0, 0, elementDiagramCanvas.width, elementDiagramCanvas.height);
        if(elementDiagramPlaceholder) elementDiagramPlaceholder.style.display = 'none';
        const L_px = elementDiagramCanvas.width * 0.8;
        const L_m = element_info.length_m;
        const scale = L_m > 0 ? L_px / L_m : L_px;
        const margin_x = elementDiagramCanvas.width * 0.1;
        const y_beam_centerline = elementDiagramCanvas.height * 0.4;
        const y_deflected_beam_center = elementDiagramCanvas.height * 0.75;
        let section_depth_m = 0.1;
        if (element_info.cross_section.cy_top_m !== undefined && element_info.cross_section.cy_bottom_m !== undefined) section_depth_m = element_info.cross_section.cy_top_m + element_info.cross_section.cy_bottom_m;
        else if (element_info.cross_section.type.toLowerCase() === "circular" && element_info.cross_section.cx_right_m !== undefined) section_depth_m = 2 * element_info.cross_section.cx_right_m;
        const beam_thickness_px = Math.max(10, Math.min(30, section_depth_m * scale * 0.35 + 6));

        const moment_values = results.bmd_points ? results.bmd_points.map(p => p.m || 0) : [];
        const max_abs_moment_val = moment_values.length > 0 ? Math.max(...moment_values.map(m => Math.abs(m))) : 0;
        if (max_abs_moment_val > 0 && results.bmd_points) {
            for (let i = 0; i < results.bmd_points.length - 1; i++) {
                const p1 = results.bmd_points[i]; const p2 = results.bmd_points[i+1];
                const x1_px = margin_x + (p1.x || 0) * scale; const x2_px = margin_x + (p2.x || 0) * scale;
                const segment_moment_avg = (p1.m + p2.m) / 2;
                const color = getColorForMomentGradient(Math.abs(segment_moment_avg), 0, max_abs_moment_val);
                elementCtx.fillStyle = color;
                elementCtx.fillRect(x1_px, y_beam_centerline - beam_thickness_px / 2, (x2_px - x1_px + 1), beam_thickness_px);
            }
        }
        elementCtx.strokeStyle = themeColors.diagramSupportColor; elementCtx.lineWidth = 2;
        elementCtx.strokeRect(margin_x, y_beam_centerline - beam_thickness_px / 2, L_px, beam_thickness_px);
        elementCtx.lineWidth = 1;

        const support_size = 18;
        if (inputs.beamSupportType === 'simplySupported') {
            drawTriangleSupport(elementCtx, margin_x, y_beam_centerline + beam_thickness_px / 2, support_size, themeColors.diagramSupportColor);
            drawRollerSupport(elementCtx, margin_x + L_px, y_beam_centerline + beam_thickness_px / 2, support_size, themeColors.diagramSupportColor);
        } else if (inputs.beamSupportType === 'cantilever') {
            elementCtx.fillStyle = themeColors.diagramSupportColor;
            elementCtx.fillRect(margin_x - support_size, y_beam_centerline - beam_thickness_px*1.3, support_size, beam_thickness_px * 2.6);
            elementCtx.strokeStyle = themeColors.diagramSupportColor;
            elementCtx.strokeRect(margin_x - support_size, y_beam_centerline - beam_thickness_px*1.3, support_size, beam_thickness_px * 2.6);
            for (let i = 0; i < 6; i++) {
                elementCtx.beginPath();
                elementCtx.moveTo(margin_x - support_size, y_beam_centerline - beam_thickness_px * 1.3 + i * (beam_thickness_px * 2.6 / 5));
                elementCtx.lineTo(margin_x - support_size - 6, y_beam_centerline - beam_thickness_px * 1.3 + i * (beam_thickness_px * 2.6 / 5) + 6);
                elementCtx.stroke();
            }
        }
        const load_arrow_top_y = y_beam_centerline - beam_thickness_px / 2 - 30;
        const load_arrow_bottom_y = y_beam_centerline - beam_thickness_px / 2 - 3;
        elementCtx.textAlign = 'center'; elementCtx.font = "13px " + themeColors.fontFamily; elementCtx.fillStyle = themeColors.diagramTextColor;

        if (inputs.beamLoadType.includes('pointLoad')) {
            const load_x_ratio = inputs.beamLoadType === 'pointLoadEnd' ? 1.0 : (inputs.pointLoadPositionRatio || 0.5);
            const load_x_px = margin_x + L_px * load_x_ratio;
            drawArrow(elementCtx, load_x_px, load_arrow_top_y, load_x_px, load_arrow_bottom_y, themeColors.diagramLoadColor, 12);
            elementCtx.fillStyle = themeColors.diagramLoadColor;
            elementCtx.fillText(`${inputs.pointLoad || 0} kN`, load_x_px, load_arrow_top_y - 8);
        } else if (inputs.beamLoadType === 'udl') {
            const numArrows = Math.min(12, Math.max(5, Math.floor(L_px / 50)));
            const udlRectTopY = load_arrow_top_y + 5; const udlRectBottomY = load_arrow_bottom_y;
            elementCtx.fillStyle = themeColors.diagramUdlColor.replace(')', ', 0.15)'); // Add alpha
            elementCtx.fillRect(margin_x, udlRectTopY, L_px, udlRectBottomY - udlRectTopY);
            elementCtx.strokeStyle = themeColors.diagramUdlColor.replace(')', ', 0.6)'); // Add alpha
            elementCtx.strokeRect(margin_x, udlRectTopY, L_px, udlRectBottomY - udlRectTopY);
            const arrowSpacing = L_px / (numArrows +1) ;
            for (let i = 1; i <= numArrows; i++) {
                const arrowX = margin_x + i * arrowSpacing;
                drawArrow(elementCtx, arrowX, udlRectTopY, arrowX, udlRectBottomY, themeColors.diagramUdlColor, 7);
            }
            elementCtx.fillStyle = themeColors.diagramUdlColor;
            elementCtx.fillText(`${inputs.udlValue || 0} kN/m`, margin_x + L_px / 2, udlRectTopY - 8);
        }
        elementCtx.textAlign = 'start';

        const deflection_points = results.deflection_points;
        if (deflection_points && deflection_points.length > 0) {
            const max_abs_deflection_m = Math.max(...deflection_points.map(p => Math.abs(p.d || 0)));
            let exaggeration_factor = max_abs_deflection_m > 0 ? (elementDiagramCanvas.height * 0.20) / max_abs_deflection_m : 0;
            exaggeration_factor = Math.min(exaggeration_factor, 7000); 
            elementCtx.beginPath();
            elementCtx.moveTo(margin_x + (deflection_points[0].x || 0) * scale, y_deflected_beam_center + (deflection_points[0].d || 0) * exaggeration_factor);
            for (let i = 1; i < deflection_points.length; i++) elementCtx.lineTo(margin_x + (deflection_points[i].x || 0) * scale, y_deflected_beam_center + (deflection_points[i].d || 0) * exaggeration_factor);
            elementCtx.strokeStyle = themeColors.diagramDeflectedShapeColor + 'AA';
            elementCtx.lineWidth = 2.5; elementCtx.stroke(); elementCtx.lineWidth = 1;
        }
        elementCtx.strokeStyle = themeColors.diagramDimensionLineColor; elementCtx.lineWidth = 0.75;
        const dimY = y_beam_centerline + beam_thickness_px / 2 + support_size + 25;
        elementCtx.beginPath(); elementCtx.moveTo(margin_x, dimY - 5); elementCtx.lineTo(margin_x, dimY + 5);
        elementCtx.moveTo(margin_x + L_px, dimY - 5); elementCtx.lineTo(margin_x + L_px, dimY + 5);
        elementCtx.moveTo(margin_x, dimY); elementCtx.lineTo(margin_x + L_px, dimY); elementCtx.stroke();
        elementCtx.fillStyle = themeColors.diagramDimensionLineColor; elementCtx.textAlign = 'center';
        elementCtx.font = "12px " + themeColors.fontFamily;
        elementCtx.fillText(`L = ${L_m.toFixed(1)} m`, margin_x + L_px / 2, dimY - 8);
        elementCtx.textAlign = 'start';
    }

    function drawColumnDiagram(element_info, results, inputs) {
        elementCtx.clearRect(0, 0, elementDiagramCanvas.width, elementDiagramCanvas.height);
        if(elementDiagramPlaceholder) elementDiagramPlaceholder.style.display = 'none';
        const H_px = elementDiagramCanvas.height * 0.75; const H_m = element_info.length_m;
        const scale_y = H_m > 0 ? H_px / H_m : H_px;
        const x_col_center = elementDiagramCanvas.width * 0.5;
        const margin_y_top = elementDiagramCanvas.height * 0.1;
        let section_width_m = 0.05;
        if (element_info.cross_section.cx_left_m !== undefined && element_info.cross_section.cx_right_m !== undefined) section_width_m = element_info.cross_section.cx_left_m + element_info.cross_section.cx_right_m;
        else if (element_info.cross_section.type.toLowerCase() === "circular" && element_info.cross_section.cx_right_m !== undefined) section_width_m = 2 * element_info.cross_section.cx_right_m;
        const col_width_px = Math.max(12, Math.min(45, section_width_m * scale_y * 0.6 + 8));

        const axial_stress_Pa = results.axial_stress_Pa || 0;
        const yield_strength_Pa = element_info.material.Fy_Pa || Infinity;
        if (yield_strength_Pa > 0 && yield_strength_Pa !== Infinity) {
            const color = getColorForStress(-axial_stress_Pa, yield_strength_Pa);
            elementCtx.fillStyle = color;
            elementCtx.fillRect(x_col_center - col_width_px / 2, margin_y_top, col_width_px, H_px);
        } else {
            elementCtx.fillStyle = themeColors.mutedText.replace(')', ', 0.3)'); // Default grey translucent
            elementCtx.fillRect(x_col_center - col_width_px / 2, margin_y_top, col_width_px, H_px);
        }
        elementCtx.strokeStyle = themeColors.diagramSupportColor; elementCtx.lineWidth = 2;
        elementCtx.strokeRect(x_col_center - col_width_px / 2, margin_y_top, col_width_px, H_px);
        elementCtx.lineWidth = 1;

        const support_size = 18;
        drawTriangleSupport(elementCtx, x_col_center, margin_y_top + H_px + support_size / 2, support_size, themeColors.diagramSupportColor, 'bottom');
        drawTriangleSupport(elementCtx, x_col_center, margin_y_top - support_size / 2, support_size, themeColors.diagramSupportColor, 'top');
        drawArrow(elementCtx, x_col_center, margin_y_top - 30, x_col_center, margin_y_top -3, themeColors.diagramLoadColor, 12);
        elementCtx.fillStyle = themeColors.diagramLoadColor; elementCtx.textAlign = 'center';
        elementCtx.font = "13px " + themeColors.fontFamily;
        elementCtx.fillText(`${inputs.axialLoad || 0} kN`, x_col_center, margin_y_top - 38);
        elementCtx.textAlign = 'start';

        const P_applied = (inputs.axialLoad || 0) * 1000;
        const P_crit = results.min_critical_buckling_load_N || 0;
        let buckling_mode_visible = false;
        if(results.failure_checks && results.failure_checks.euler_buckling && results.failure_checks.euler_buckling.ratio > 0.3 && P_crit > 0) buckling_mode_visible = true;
        
        if (buckling_mode_visible) {
            const buckling_exaggeration_px = col_width_px * 1.8 * Math.min(1.8, P_applied / P_crit);
            elementCtx.beginPath(); elementCtx.moveTo(x_col_center, margin_y_top);
            let K_factor_for_shape_approx = Math.min(element_info.Kx, element_info.Ky);
            if (K_factor_for_shape_approx <= 0.6) for (let y_rel = 0; y_rel <= H_px; y_rel++) elementCtx.lineTo(x_col_center + buckling_exaggeration_px * 0.5 * (1 - Math.cos(2 * Math.PI * (y_rel / H_px))), margin_y_top + y_rel);
            else if (K_factor_for_shape_approx >= 1.8) for (let y_rel = 0; y_rel <= H_px; y_rel++) elementCtx.lineTo(x_col_center + buckling_exaggeration_px * (1 - Math.cos( (Math.PI / 2) * (y_rel / H_px))), margin_y_top + y_rel);
            else for (let y_rel = 0; y_rel <= H_px; y_rel++) elementCtx.lineTo(x_col_center + buckling_exaggeration_px * Math.sin(Math.PI * (y_rel / H_px)), margin_y_top + y_rel);
            elementCtx.strokeStyle = themeColors.diagramBuckledShapeColor + 'AA';
            elementCtx.lineWidth = 2.5; elementCtx.stroke(); elementCtx.lineWidth = 1;
        }
        elementCtx.strokeStyle = themeColors.diagramDimensionLineColor; elementCtx.lineWidth = 0.75;
        const dimX = x_col_center + col_width_px / 2 + 25;
        elementCtx.beginPath(); elementCtx.moveTo(dimX - 5, margin_y_top); elementCtx.lineTo(dimX + 5, margin_y_top);
        elementCtx.moveTo(dimX - 5, margin_y_top + H_px); elementCtx.lineTo(dimX + 5, margin_y_top + H_px);
        elementCtx.moveTo(dimX, margin_y_top); elementCtx.lineTo(dimX, margin_y_top + H_px); elementCtx.stroke();
        elementCtx.fillStyle = themeColors.diagramDimensionLineColor; elementCtx.textAlign = 'center';
        elementCtx.font = "12px " + themeColors.fontFamily;
        elementCtx.save(); elementCtx.translate(dimX + 8, margin_y_top + H_px / 2);
        elementCtx.rotate(-Math.PI / 2); elementCtx.fillText(`H = ${H_m.toFixed(1)} m`, 0, 0);
        elementCtx.restore(); elementCtx.textAlign = 'start';
    }

    function drawTriangleSupport(ctx, x, y, size, color, orientation = 'bottom') {
        ctx.beginPath();
        if (orientation === 'bottom') { ctx.moveTo(x - size, y); ctx.lineTo(x + size, y); ctx.lineTo(x, y - size); }
        else { ctx.moveTo(x - size, y); ctx.lineTo(x + size, y); ctx.lineTo(x, y + size); }
        ctx.closePath(); ctx.fillStyle = color; ctx.fill();
        if (orientation === 'bottom') {
            ctx.strokeStyle = color; ctx.lineWidth = 0.8;
            for (let i = 0; i < 5; i++) {
                ctx.beginPath(); const startX = x - size + (i * (2 * size / 4));
                ctx.moveTo(startX, y); ctx.lineTo(startX - size/3, y + size/3); ctx.stroke();
            }
            ctx.lineWidth = 1;
        }
    }
    function drawRollerSupport(ctx, x, y, size, color) {
        drawTriangleSupport(ctx, x, y, size, color);
        const rollerRadius = size / 3; const rollerYOffset = size / 2.2;
        ctx.beginPath(); ctx.arc(x - size/2 + rollerRadius/2 , y + rollerYOffset, rollerRadius, 0, 2 * Math.PI); ctx.fill();
        ctx.beginPath(); ctx.arc(x + size/2 - rollerRadius/2, y + rollerYOffset, rollerRadius, 0, 2 * Math.PI); ctx.fill();
        ctx.beginPath(); ctx.moveTo(x - size * 1.2, y + rollerYOffset + rollerRadius + 3);
        ctx.lineTo(x + size * 1.2, y + rollerYOffset + rollerRadius + 3);
        ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke(); ctx.lineWidth = 1;
    }

    function drawArrow(ctx, fromx, fromy, tox, toy, color, headlen) {
        const dx = tox - fromx; const dy = toy - fromy; const angle = Math.atan2(dy, dx);
        ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = 2.5;
        ctx.beginPath(); ctx.moveTo(fromx, fromy); ctx.lineTo(tox, toy); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(tox, toy);
        ctx.lineTo(tox - headlen * Math.cos(angle - Math.PI / 6), toy - headlen * Math.sin(angle - Math.PI / 6));
        ctx.lineTo(tox - headlen * Math.cos(angle + Math.PI / 6), toy - headlen * Math.sin(angle + Math.PI / 6));
        ctx.closePath(); ctx.fill(); ctx.lineWidth = 1;
    }

    function drawCrossSectionStress(element_info, results, elementType) {
        csCtx.clearRect(0, 0, crossSectionCanvas.width, crossSectionCanvas.height);
        if(csCanvasPlaceholder) csCanvasPlaceholder.style.display = 'none';
        crossSectionStressInfoDiv.innerHTML = ''; // Clear previous text

        const cs = element_info.cross_section; const material = element_info.material;
        const canvasWidth = crossSectionCanvas.width; const canvasHeight = crossSectionCanvas.height;
        const margin = 25; const availableWidth = canvasWidth - 2 * margin; const availableHeight = canvasHeight - 2 * margin;
        let scale, cs_width_px, cs_height_px, origin_x, origin_y;
        let stressText = `<h4>Stress Distribution (${toTitleCase(cs.type || 'N/A')})</h4>`;
        const num_gradient_strips = 60;
        csCtx.font = "11px " + themeColors.fontFamily; csCtx.fillStyle = themeColors.diagramTextColor;

        if (cs.type.toLowerCase() === "rectangular") {
            const b_m = (cs.cx_left_m || 0) + (cs.cx_right_m || 0); const h_m = (cs.cy_top_m || 0) + (cs.cy_bottom_m || 0);
            if (b_m === 0 || h_m === 0) { stressText += "<p>Invalid section dimensions.</p>"; crossSectionStressInfoDiv.innerHTML = stressText; return; }
            scale = Math.min(availableWidth / b_m, availableHeight / h_m) * 0.85;
            cs_width_px = b_m * scale; cs_height_px = h_m * scale;
            origin_x = canvasWidth / 2; origin_y = canvasHeight / 2;
            csCtx.strokeStyle = themeColors.diagramSupportColor; csCtx.lineWidth = 2;
            csCtx.strokeRect(origin_x - cs_width_px / 2, origin_y - cs_height_px / 2, cs_width_px, cs_height_px);
        } else if (cs.type.toLowerCase() === "circular") {
            const d_m = (cs.cx_left_m || 0) + (cs.cx_right_m || 0);
            if (d_m === 0) { stressText += "<p>Invalid section dimensions.</p>"; crossSectionStressInfoDiv.innerHTML = stressText; return; }
            scale = Math.min(availableWidth / d_m, availableHeight / d_m) * 0.85;
            const r_px = (d_m / 2) * scale;
            cs_width_px = cs_height_px = 2 * r_px;
            origin_x = canvasWidth / 2; origin_y = canvasHeight / 2;
            csCtx.strokeStyle = themeColors.diagramSupportColor; csCtx.lineWidth = 2;
            csCtx.beginPath(); csCtx.arc(origin_x, origin_y, r_px, 0, 2 * Math.PI); csCtx.stroke();
        } else { stressText += "<p>Cross-section type not drawable yet.</p>"; crossSectionStressInfoDiv.innerHTML = stressText; return; }

        csCtx.strokeStyle = themeColors.diagramNeutralAxisColor; csCtx.setLineDash([3, 3]); csCtx.lineWidth = 1.5;
        csCtx.beginPath(); csCtx.moveTo(origin_x - cs_width_px / 2 - 15, origin_y); csCtx.lineTo(origin_x + cs_width_px / 2 + 15, origin_y); csCtx.stroke();
        csCtx.fillStyle = themeColors.diagramNeutralAxisColor;
        csCtx.fillText("NA (X)", origin_x + cs_width_px / 2 + 18, origin_y + 4);
        csCtx.setLineDash([]); csCtx.lineWidth = 1;

        if (elementType === 'beam') {
            const M_max_abs_val = Math.max(Math.abs(results.max_moment_Nm || 0), Math.abs(results.min_moment_Nm || 0));
            const sigma_max_abs_val = Math.max(Math.abs(results.max_bending_stress_Pa || 0), Math.abs(results.min_bending_stress_Pa || 0));
            let M_for_viz = results.max_moment_Nm || 0;
            if (results.min_moment_Nm && Math.abs(results.min_moment_Nm) > Math.abs(M_for_viz)) M_for_viz = results.min_moment_Nm;
            if (M_max_abs_val === 0) M_for_viz = 0;

            stressText += `<p><strong>Governing Moment (Viz):</strong> ${(M_for_viz/1000).toFixed(2)} kNm</p>`;
            stressText += `<p><strong>Max Bending Stress (abs):</strong> ${(sigma_max_abs_val/1e6).toFixed(2)} MPa</p>`;
            if (sigma_max_abs_val > 0 && cs.Ix_m4 > 0) {
                const y_top_m = cs.cy_top_m || 0; const y_bottom_m = cs.cy_bottom_m || 0;
                for (let i = 0; i < num_gradient_strips; i++) {
                    const y_norm_strip = (i + 0.5) / num_gradient_strips;
                    const y_m_from_na = -y_bottom_m + y_norm_strip * (y_top_m + y_bottom_m);
                    const sigma_Pa = - (M_for_viz * y_m_from_na) / cs.Ix_m4;
                    const color = getColorForStress(sigma_Pa, sigma_max_abs_val || material.Fy_Pa);
                    csCtx.fillStyle = color;
                    const strip_y_center_px = origin_y - (y_m_from_na * scale);
                    const strip_height_px = ((y_top_m + y_bottom_m) * scale / num_gradient_strips) + 0.5;
                    let strip_width_px = cs_width_px;
                    if (cs.type.toLowerCase() === "circular") {
                        const r_section_m = (cs.cx_right_m || 0);
                        strip_width_px = Math.abs(y_m_from_na) <= r_section_m ? 2 * Math.sqrt(r_section_m**2 - y_m_from_na**2) * scale : 0;
                    }
                    if (strip_width_px > 0) csCtx.fillRect(origin_x - strip_width_px / 2, strip_y_center_px - strip_height_px / 2, strip_width_px, strip_height_px);
                }
                 csCtx.strokeStyle = themeColors.diagramSupportColor; csCtx.lineWidth = 2;
                 if (cs.type.toLowerCase() === "rectangular") csCtx.strokeRect(origin_x - cs_width_px / 2, origin_y - cs_height_px / 2, cs_width_px, cs_height_px);
                 if (cs.type.toLowerCase() === "circular") { csCtx.beginPath(); csCtx.arc(origin_x, origin_y, (cs.cx_right_m || 0)*scale, 0, 2*Math.PI); csCtx.stroke(); }
            }
            const sigma_top_Pa = cs.Ix_m4 > 0 ? (- (M_for_viz * (cs.cy_top_m||0)) / cs.Ix_m4) : 0;
            const sigma_bottom_Pa = cs.Ix_m4 > 0 ? (- (M_for_viz * (-(cs.cy_bottom_m||0))) / cs.Ix_m4) : 0;
            stressText += `<p><strong>Top Fiber Stress:</strong> ${(sigma_top_Pa / 1e6).toFixed(2)} MPa (${sigma_top_Pa >= 0 ? 'Tension' : 'Compression'})</p>`;
            stressText += `<p><strong>Bottom Fiber Stress:</strong> ${(sigma_bottom_Pa / 1e6).toFixed(2)} MPa (${sigma_bottom_Pa >= 0 ? 'Tension' : 'Compression'})</p>`;
        } else if (elementType === 'column') {
            const axial_stress_Pa = results.axial_stress_Pa || 0;
            stressText += `<p><strong>Axial Stress:</strong> ${(axial_stress_Pa / 1e6).toFixed(2)} MPa (${axial_stress_Pa >= 0 ? 'Compression' : 'Tension'})</p>`;
            if (Math.abs(axial_stress_Pa) > 0 && material.Fy_Pa > 0) {
                const stress_for_color_viz = -axial_stress_Pa;
                const color = getColorForStress(stress_for_color_viz, material.Fy_Pa);
                csCtx.fillStyle = color;
                if (cs.type.toLowerCase() === "rectangular") {
                    csCtx.fillRect(origin_x - cs_width_px / 2, origin_y - cs_height_px / 2, cs_width_px, cs_height_px);
                    csCtx.strokeStyle = themeColors.diagramSupportColor; csCtx.lineWidth = 2; csCtx.strokeRect(origin_x - cs_width_px / 2, origin_y - cs_height_px / 2, cs_width_px, cs_height_px);
                } else if (cs.type.toLowerCase() === "circular") {
                    csCtx.beginPath(); csCtx.arc(origin_x, origin_y, ((cs.cx_right_m||0) + (cs.cx_left_m||0))/2*scale, 0, 2*Math.PI);
                    csCtx.fill();
                    csCtx.strokeStyle = themeColors.diagramSupportColor; csCtx.lineWidth = 2; csCtx.stroke();
                }
            }
        }
        crossSectionStressInfoDiv.innerHTML = stressText;
    }

    function getColorForStress(stress_Pa, max_abs_stress_Pa_scale) {
        if (max_abs_stress_Pa_scale === 0 || !themeColors.stressNeutral) return 'rgb(200,200,200)'; // Fallback if themeColors not ready
        const norm_stress = Math.max(-1, Math.min(1, stress_Pa / max_abs_stress_Pa_scale));
        
        const [neutralR, neutralG, neutralB] = themeColors.stressNeutral.match(/\d+/g).map(Number);
        const [tensionR, tensionG, tensionB] = themeColors.stressTensionMax.match(/\d+/g).map(Number);
        const [compR, compG, compB] = themeColors.stressCompressionMax.match(/\d+/g).map(Number);

        let r, g, b;
        if (norm_stress > 0) { // Tension
            r = Math.round(neutralR + (tensionR - neutralR) * norm_stress);
            g = Math.round(neutralG + (tensionG - neutralG) * norm_stress);
            b = Math.round(neutralB + (tensionB - neutralB) * norm_stress);
        } else if (norm_stress < 0) { // Compression
            const abs_norm_stress = -norm_stress;
            r = Math.round(neutralR + (compR - neutralR) * abs_norm_stress);
            g = Math.round(neutralG + (compG - neutralG) * abs_norm_stress);
            b = Math.round(neutralB + (compB - neutralB) * abs_norm_stress);
        } else { r = neutralR; g = neutralG; b = neutralB; }
        return `rgb(${Math.max(0,Math.min(255,r))},${Math.max(0,Math.min(255,g))},${Math.max(0,Math.min(255,b))})`;
    }

    function getColorForMomentGradient(value, min_val, max_val) { // Viridis-like
        let norm_value;
        if (max_val <= min_val) norm_value = 0.0; else norm_value = (value - min_val) / (max_val - min_val);
        norm_value = Math.max(0, Math.min(1, norm_value));
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        // Viridis-like: Deep Purple -> Blue -> Teal -> Green -> Yellow -> Orange/Red
        if (norm_value < 0.01) return isDark ? "rgb(68,1,84)" : "rgba(68,1,84,0.7)";
        if (norm_value < 0.2)  return isDark ? "rgb(72,39,117)" : "rgba(72,39,117,0.7)";
        if (norm_value < 0.4)  return isDark ? "rgb(59,82,139)" : "rgba(59,82,139,0.7)";
        if (norm_value < 0.6)  return isDark ? "rgb(33,145,140)" : "rgba(33,145,140,0.7)";
        if (norm_value < 0.8)  return isDark ? "rgb(94,201,98)" : "rgba(94,201,98,0.7)";
        return isDark ? "rgb(253,231,37)" : "rgba(253,231,37,0.7)"; // Yellow for high
    }

    // --- Initial Setup Calls ---
    function initializeDisplaysAndPlaceholders() {
        lengthInput.dispatchEvent(new Event('input'));
        rectWidthInput.dispatchEvent(new Event('input'));
        rectHeightInput.dispatchEvent(new Event('input'));
        circDiameterInput.dispatchEvent(new Event('input'));
        pointLoadInput.dispatchEvent(new Event('input'));
        if(udlValueInput) udlValueInput.dispatchEvent(new Event('input'));
        pointLoadPositionRatioInput.dispatchEvent(new Event('input'));
        axialLoadInput.dispatchEvent(new Event('input'));
        if(columnEndConditionSelect) columnEndConditionSelect.dispatchEvent(new Event('change'));
        else { effLengthFactorKxInput.dispatchEvent(new Event('input')); effLengthFactorKyInput.dispatchEvent(new Event('input')); }
        
        // Show initial placeholders
        placeholderTexts.forEach(el => el.style.display = 'block');
        if(elementDiagramPlaceholder) elementDiagramPlaceholder.style.display = 'block';
        if(csCanvasPlaceholder) csCanvasPlaceholder.style.display = 'block';
        if(jsonOutputPlaceholder) jsonOutputPlaceholder.style.display = 'block';
    }

    toggleElementInputs();
    toggleSectionParams();
    initializeDisplaysAndPlaceholders();
});