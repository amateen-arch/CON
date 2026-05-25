// notebookConfig.js

// Page Canvas Dimensions
const PAGE_WIDTH = 800;
const PAGE_HEIGHT = 1130;

// CHANGED: Widened the text boundaries
const MARGIN_LEFT = 67;   // Decreased from 95 to start closer to the left edge
const MARGIN_RIGHT = 765;  // Increased from 740 to extend closer to the right edge

/**
 * Advanced Multi-Axis Hardcoded Coordinates Grid Map.
 */
const NOTEBOOK_LINES = [
    // ... leave your refined array exactly as it is below this ...
    // --- TOP MARGIN ZONE LINES ---
    { yStart: 122, tiltOffset: 0 },  // Line 1
    { yStart: 172, tiltOffset: -0.6 },  // Line 2
    
    // --- MAIN REGISTER BODY LINES ---
    { yStart: 218, tiltOffset: -0.9 },  // Line 3
    { yStart: 264, tiltOffset: -1.2 },  // Line 4
    { yStart: 308, tiltOffset: 0.3 },  // Line 5
    { yStart: 353, tiltOffset: 0.3 },  // Line 6
    { yStart: 398, tiltOffset: -0.9 },  // Line 7
    { yStart: 445, tiltOffset: -1.9 },  // Line 8
    { yStart: 488, tiltOffset: 0.2 },  // Line 9
    { yStart: 535, tiltOffset: -2.2 },  // Line 10
    { yStart: 581, tiltOffset: -2.2 },  // Line 11
    
    // --- HIGH-DRIFT SKEW ZONE ---
    { yStart: 627, tiltOffset: -3 },  // Line 12
    { yStart: 673, tiltOffset: -4 },  // Line 13
    { yStart: 719, tiltOffset: -4 },  // Line 14
    { yStart: 765, tiltOffset: -4 },  // Line 15
    { yStart: 811, tiltOffset: -3 },  // Line 16
    { yStart: 857, tiltOffset: -4 }, // Line 17
    { yStart: 903, tiltOffset: -3 }, // Line 18
    { yStart: 949, tiltOffset: -3.5 },  // Line 19
    { yStart: 995, tiltOffset: -3 },  // Line 20
    { yStart: 1041, tiltOffset: -3 }, // Line 21
    { yStart: 1088, tiltOffset: -2 }, // Line 22
    { yStart: 1134, tiltOffset: 2 }  // Line 23
];

const TOTAL_LINES_PER_PAGE = 22;