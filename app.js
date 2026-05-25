// app.js

// Core Document Data Storage Layer
let documentCharacterStream = [];
let cursorCharacterIndex = 0;

// Global Application Core Configuration Parameters
let activeInkColor = "#0c1c5e";
let currentDocumentPagesCount = 0;
let primaryFocusedPageIndex = 1;
let systemCursorBlinkState = true;
let cursorIntervalTimer = null;
let virtualColumnGoalX = 0; // Tracks your intended horizontal position across line changes

const registerPaperTemplate = new Image();
registerPaperTemplate.src = "assets/register_bg.png";

/**
 * Object Model representing individual pages inside the stack.
 */
class DocumentPageLayer {
    constructor(pageNumber) {
        this.pageNumber = pageNumber;
        this.buildDOMElements();
    }

    buildDOMElements() {
        const stackContainer = document.getElementById("canvasPageStack");

        this.wrapper = document.createElement("div");
        this.wrapper.className = "page-wrapper";
        this.wrapper.id = `pageWrapper-${this.pageNumber}`;

        this.canvas = document.createElement("canvas");
        this.canvas.className = "register-sheet";
        this.canvas.id = `assignmentCanvas-${this.pageNumber}`;
        this.canvas.width = PAGE_WIDTH;
        this.canvas.height = PAGE_HEIGHT;
        
        this.ctx = this.canvas.getContext("2d");
        this.wrapper.appendChild(this.canvas);
        stackContainer.appendChild(this.wrapper);
    }

    clearAndPaintBackground() {
        this.ctx.fillStyle = "#fffdf5";
        this.ctx.fillRect(0, 0, PAGE_WIDTH, PAGE_HEIGHT);
        
        if (registerPaperTemplate.complete && registerPaperTemplate.naturalWidth !== 0) {
            this.ctx.drawImage(registerPaperTemplate, 0, 0, PAGE_WIDTH, PAGE_HEIGHT);
        }
    }
}

let activePageInstancesList = [];

function expandDocumentLayoutStructure() {
    const nextIndex = activePageInstancesList.length + 1;
    const newPageInstance = new DocumentPageLayer(nextIndex);
    activePageInstancesList.push(newPageInstance);
    currentDocumentPagesCount = activePageInstancesList.length;
    refreshPageCounterDisplay();
    return true;
}

/**
 * Master Text Layout Wrapping Engine & Drawing Matrix
 */
function rebuildAndRenderDocumentLayout() {
    let freshPageSpawned = false;

    if (activePageInstancesList.length === 0) {
        expandDocumentLayoutStructure();
        freshPageSpawned = true;
    }

    activePageInstancesList.forEach(page => page.clearAndPaintBackground());

    let currentLineIndex = 0;
    let localLineIndex = 0;
    let pageIndex = 0;
    let currentLineX = MARGIN_LEFT;

    const layoutCtx = activePageInstancesList[0].ctx;
    layoutCtx.font = "21px Arial";
    layoutCtx.textBaseline = "alphabetic";

    let targetCursorX = MARGIN_LEFT;
    
    // Fallback assignment tracking from line 0 profile configurations
    let initialLineConfig = NOTEBOOK_LINES[0];
    let targetCursorY = initialLineConfig.yStart + 2;
    let targetCursorPageIndex = 0;

    if (cursorCharacterIndex === 0) {
        targetCursorX = MARGIN_LEFT;
        targetCursorY = initialLineConfig.yStart + 2;
        targetCursorPageIndex = 0;
    }

    for (let i = 0; i < documentCharacterStream.length; i++) {
        const charNode = documentCharacterStream[i];
        
        if (charNode.char === "\n") {
            currentLineIndex++;
            currentLineX = MARGIN_LEFT;
            
            localLineIndex = currentLineIndex % TOTAL_LINES_PER_PAGE;
            pageIndex = Math.floor(currentLineIndex / TOTAL_LINES_PER_PAGE);

            if (cursorCharacterIndex === i + 1) {
                const lineConfig = NOTEBOOK_LINES[localLineIndex];
                targetCursorX = currentLineX;
                targetCursorY = lineConfig.yStart + 2;
                targetCursorPageIndex = pageIndex;
            }
            continue;
        }

        const charWidth = layoutCtx.measureText(charNode.char).width;

        let isWordStart = (charNode.char !== ' ') && (i === 0 || documentCharacterStream[i - 1].char === ' ' || documentCharacterStream[i - 1].char === '\n');
        if (isWordStart) {
            let wordEnd = i;
            let projectedWordWidth = 0;
            while (wordEnd < documentCharacterStream.length && documentCharacterStream[wordEnd].char !== ' ' && documentCharacterStream[wordEnd].char !== '\n') {
                projectedWordWidth += layoutCtx.measureText(documentCharacterStream[wordEnd].char).width;
                wordEnd++;
            }
            
            if (currentLineX + projectedWordWidth > MARGIN_RIGHT && currentLineX > MARGIN_LEFT) {
                currentLineIndex++;
                currentLineX = MARGIN_LEFT;
            }
        }

        if (currentLineX + charWidth > MARGIN_RIGHT) {
            currentLineIndex++;
            currentLineX = MARGIN_LEFT;
        }

        localLineIndex = currentLineIndex % TOTAL_LINES_PER_PAGE;
        pageIndex = Math.floor(currentLineIndex / TOTAL_LINES_PER_PAGE);

        while (pageIndex >= activePageInstancesList.length) {
            expandDocumentLayoutStructure();
            freshPageSpawned = true;
        }

        const targetPage = activePageInstancesList[pageIndex];
        
        targetPage.ctx.font = "21px Arial";
        targetPage.ctx.textBaseline = "alphabetic";
        targetPage.ctx.fillStyle = charNode.color;
        
        // --- DYNAMIC TILT COMPENSATION ENGINE ---
        const lineConfig = NOTEBOOK_LINES[localLineIndex];
        const lineWidthCoverage = MARGIN_RIGHT - MARGIN_LEFT;
        const currentProgressX = (currentLineX - MARGIN_LEFT) / lineWidthCoverage;
        const dynamicTiltCorrection = currentProgressX * lineConfig.tiltOffset;
        
        // Render text tracking perfectly across the physical line warp slant
        const drawY = lineConfig.yStart + 2 + dynamicTiltCorrection; 
        targetPage.ctx.fillText(charNode.char, currentLineX, drawY);

        currentLineX += charWidth;

        if (cursorCharacterIndex === i + 1) {
            targetCursorX = currentLineX;
            targetCursorY = lineConfig.yStart + 2 + dynamicTiltCorrection;
            targetCursorPageIndex = pageIndex;
        }
    }

    // Dynamic rendering calculation logic for cursor placement positioning alignment
    if (systemCursorBlinkState && activePageInstancesList[targetCursorPageIndex]) {
        const cPage = activePageInstancesList[targetCursorPageIndex];
        cPage.ctx.strokeStyle = activeInkColor;
        cPage.ctx.lineWidth = 2;
        cPage.ctx.beginPath();
        cPage.ctx.moveTo(targetCursorX, targetCursorY - 22);
        cPage.ctx.lineTo(targetCursorX, targetCursorY - 1);
        cPage.ctx.stroke();
    }

    if (freshPageSpawned && activePageInstancesList.length > 1) {
        const newestWrapper = document.getElementById(`pageWrapper-${activePageInstancesList.length}`);
        if (newestWrapper) {
            newestWrapper.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
}

function handleDocumentTypingInput(e) {
    let changed = false;
    let movedVertically = false;
    if (e.ctrlKey || e.metaKey) return;

    if (e.key === "Backspace") {
        if (cursorCharacterIndex > 0) {
            documentCharacterStream.splice(cursorCharacterIndex - 1, 1);
            cursorCharacterIndex--;
            changed = true;
        }
    } else if (e.key === "Delete") {
        if (cursorCharacterIndex < documentCharacterStream.length) {
            documentCharacterStream.splice(cursorCharacterIndex, 1);
            changed = true;
        }
    } else if (e.key === "ArrowLeft") {
        if (cursorCharacterIndex > 0) {
            cursorCharacterIndex--;
            changed = true;
        }
    } else if (e.key === "ArrowRight") {
        if (cursorCharacterIndex < documentCharacterStream.length) {
            cursorCharacterIndex++;
            changed = true;
        }
    } else if (e.key === "ArrowUp" || e.key === "ArrowDown") {
        movedVertically = true;

        // --- VERTICAL LINE NAVIGATION ENGINE ---
        const layoutCtx = activePageInstancesList[0].ctx;
        layoutCtx.font = "21px Arial";
        layoutCtx.textBaseline = "alphabetic";

        let lineMap = []; 
        let currentLineArray = [];
        let currentX = MARGIN_LEFT;

        // Build character matrix map
        for (let i = 0; i < documentCharacterStream.length; i++) {
            const charNode = documentCharacterStream[i];
            
            if (charNode.char === "\n") {
                lineMap.push(currentLineArray);
                currentLineArray = [];
                currentX = MARGIN_LEFT;
                continue;
            }

            const charWidth = layoutCtx.measureText(charNode.char).width;

            let isWordStart = (charNode.char !== ' ') && (i === 0 || documentCharacterStream[i - 1].char === ' ' || documentCharacterStream[i - 1].char === '\n');
            if (isWordStart) {
                let wordEnd = i;
                let projectedWordWidth = 0;
                while (wordEnd < documentCharacterStream.length && documentCharacterStream[wordEnd].char !== ' ' && documentCharacterStream[wordEnd].char !== '\n') {
                    projectedWordWidth += layoutCtx.measureText(documentCharacterStream[wordEnd].char).width;
                    wordEnd++;
                }
                if (currentX + projectedWordWidth > MARGIN_RIGHT && currentX > MARGIN_LEFT) {
                    lineMap.push(currentLineArray);
                    currentLineArray = [];
                    currentX = MARGIN_LEFT;
                }
            }

            if (currentX + charWidth > MARGIN_RIGHT) {
                lineMap.push(currentLineArray);
                currentLineArray = [];
                currentX = MARGIN_LEFT;
            }

            currentLineArray.push(i);
            currentX += charWidth;
        }
        lineMap.push(currentLineArray);

        // Find current cursor line row mapping
        let currentCursorLineIdx = 0;
        let positionInLine = 0;

        for (let l = 0; l < lineMap.length; l++) {
            if (lineMap[l].includes(cursorCharacterIndex)) {
                currentCursorLineIdx = l;
                positionInLine = lineMap[l].indexOf(cursorCharacterIndex);
                break;
            } else if (lineMap[l].length > 0 && cursorCharacterIndex === lineMap[l][lineMap[l].length - 1] + 1) {
                currentCursorLineIdx = l;
                positionInLine = lineMap[l].length;
                break;
            }
        }

        // Initialize virtual column memory if this is the first vertical movement
        if (typeof virtualColumnGoalX === "undefined" || virtualColumnGoalX === null || virtualColumnGoalX === 0) {
            virtualColumnGoalX = positionInLine;
        }

        // Apply line adjustment
        let targetLineIdx = currentCursorLineIdx;
        if (e.key === "ArrowUp") {
            targetLineIdx = Math.max(0, currentCursorLineIdx - 1);
        } else {
            targetLineIdx = Math.min(lineMap.length - 1, currentCursorLineIdx + 1);
        }

        if (targetLineIdx !== currentCursorLineIdx) {
            const targetLine = lineMap[targetLineIdx];
            if (targetLine.length === 0) {
                if (targetLineIdx > 0 && lineMap[targetLineIdx - 1].length > 0) {
                    cursorCharacterIndex = lineMap[targetLineIdx - 1][lineMap[targetLineIdx - 1].length - 1] + 1;
                } else {
                    cursorCharacterIndex = 0;
                }
            } else {
                let targetPos = Math.min(virtualColumnGoalX, targetLine.length - 1);
                cursorCharacterIndex = targetLine[targetPos];
                
                if (virtualColumnGoalX >= targetLine.length) {
                    cursorCharacterIndex = targetLine[targetLine.length - 1] + 1;
                }
            }
            changed = true;
        }

    } else if (e.key === "Enter") {
        documentCharacterStream.splice(cursorCharacterIndex, 0, { char: "\n", color: activeInkColor });
        cursorCharacterIndex++;
        changed = true;
    } else if (e.key.length === 1) {
        documentCharacterStream.splice(cursorCharacterIndex, 0, { char: e.key, color: activeInkColor });
        cursorCharacterIndex++;
        changed = true;
    }

    // Reset column memory if you actually type or move left/right manually
    if (changed && !movedVertically) {
        virtualColumnGoalX = 0; 
    }

    if (changed) {
        systemCursorBlinkState = true;
        rebuildAndRenderDocumentLayout();
    }
}

function initializeClipboardSystem() {
    window.addEventListener("copy", (e) => {
        e.preventDefault();
        const fullPlainText = documentCharacterStream.map(node => node.char).join("");
        if (fullPlainText.length > 0) {
            e.clipboardData.setData("text/plain", fullPlainText);
        }
    });

    window.addEventListener("paste", (e) => {
        e.preventDefault();
        const pastedText = e.clipboardData.getData("text/plain");
        
        if (pastedText && pastedText.length > 0) {
            const charactersToInject = pastedText.split("").map(char => ({
                char: char,
                color: activeInkColor
            }));
            documentCharacterStream.splice(cursorCharacterIndex, 0, ...charactersToInject);
            cursorCharacterIndex += charactersToInject.length;

            systemCursorBlinkState = true;
            rebuildAndRenderDocumentLayout();
        }
    });
}

function initializeColorSelectionSystem() {
    const swatches = document.querySelectorAll(".color-swatch");
    swatches.forEach(swatch => {
        swatch.addEventListener("click", (e) => {
            e.stopPropagation();
            document.querySelector(".color-swatch.active").classList.remove("active");
            swatch.classList.add("active");
            activeInkColor = swatch.getAttribute("data-color");
            
            systemCursorBlinkState = true;
            rebuildAndRenderDocumentLayout();
            document.getElementById("hiddenDocumentCaptureInput").focus();
        });
    });
}

function initializeGlobalFocusGuardian() {
    const inputCapture = document.getElementById("hiddenDocumentCaptureInput");
    window.addEventListener("click", () => {
        inputCapture.focus();
    });
}

function startCursorBlinkTimer() {
    if (cursorIntervalTimer) clearInterval(cursorIntervalTimer);
    cursorIntervalTimer = setInterval(() => {
        systemCursorBlinkState = !systemCursorBlinkState;
        rebuildAndRenderDocumentLayout();
    }, 530);
}

function refreshPageCounterDisplay() {
    const counterElement = document.getElementById("globalPageCounter");
    if (counterElement) {
        counterElement.textContent = `Page ${primaryFocusedPageIndex} of ${currentDocumentPagesCount}`;
    }
}

function trackViewportScrollProgress() {
    const viewport = document.getElementById("scrollViewport");
    const wrappers = document.querySelectorAll(".page-wrapper");
    
    let primaryVisiblePageIdx = 1;
    let maximumVisibleSegmentArea = 0;

    wrappers.forEach((wrapperNode, idx) => {
        const bounds = wrapperNode.getBoundingClientRect();
        const vBounds = viewport.getBoundingClientRect();

        const overlapTop = Math.max(bounds.top, vBounds.top);
        const overlapBottom = Math.min(bounds.bottom, vBounds.bottom);
        const visibleHeight = overlapBottom - overlapTop;

        if (visibleHeight > maximumVisibleSegmentArea) {
            maximumVisibleSegmentArea = visibleHeight;
            primaryVisiblePageIdx = idx + 1;
        }
    });

    if (primaryVisiblePageIdx !== primaryFocusedPageIndex && primaryVisiblePageIdx > 0) {
        primaryFocusedPageIndex = primaryVisiblePageIdx;
        refreshPageCounterDisplay();
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const viewportNode = document.getElementById("scrollViewport");
    const inputCapture = document.getElementById("hiddenDocumentCaptureInput");

    viewportNode.addEventListener("scroll", trackViewportScrollProgress);
    inputCapture.addEventListener("keydown", handleDocumentTypingInput);

    initializeColorSelectionSystem();
    initializeGlobalFocusGuardian();
    initializeClipboardSystem();
    startCursorBlinkTimer();

    // Safely verify if asset has loaded into cache
    registerPaperTemplate.onload = () => {
        rebuildAndRenderDocumentLayout();
    };

    if (registerPaperTemplate.complete) {
        rebuildAndRenderDocumentLayout();
    }

    inputCapture.focus();
});

