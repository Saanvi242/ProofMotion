"""Shared ProofMotion colors, typography, and Qt stylesheet."""

import sys
from PyQt5.QtGui import QFont, QFontDatabase

COLORS = {
    "bg_app": "#F6F7FB",
    "bg_panel": "#FFFFFF",
    "bg_panel_alt": "#F8F9FD",
    "bg_input": "#F7F8FC",
    "bg_viewport": "#F8F9FD",
    "border_workspace": "#D5DDED",
    "border_canvas": "#E0E6F2",
    "border_sidebar": "#E1E6F0",
    "border": "#E2E8F0",
    "border_soft": "#EEF0F5",
    "border_focus": "#6C5CE7",
    "text_primary": "#0F172A",
    "text_secondary": "#475569",
    "text_muted": "#64748B",
    "text_on_accent": "#FFFFFF",
    "accent_gold": "#6C5CE7",
    "accent_gold_hover": "#5946C8",
    "accent_gold_pressed": "#4D3BB8",
    "accent_teal": "#6C5CE7",
    "accent_teal_hover": "#5946C8",
    "accent_teal_pressed": "#4D3BB8",
    "accent_blue": "#526CCB",
    "danger": "#D65362",
    "success": "#2F9E78",
    "geo_stroke": "#E6E9F1",
    "geo_stroke_soft": "#F0F2F7",
    "grid_line": "#EDF0F7",
    "axis_line": "#D0D7E5",
    "selected_bg": "#EAE6FF",
}

FONT_FAMILY = "Inter"
FONT_FAMILY_MONO = '"Menlo", "Consolas", "Courier New", monospace'

TYPOGRAPHY = {
    "wordmark": 22,        # Bold (700)
    "panel_title": 18,     # Semibold (600)
    "step_title": 15,      # Semibold (600)
    "equation": 15,        # Monospace regular/medium
    "nav_label": 14,       # Medium (500)
    "body": 14,            # Regular (400)
    "param_label": 14,     # Medium (500)
    "button": 14,          # Semibold (600) / Medium (500)
    "toolbar": 13,         # Medium (500)
    "step_badge": 13,      # Semibold (600)
    "preset_chip": 12.5,   # Medium (500)
    "input": 13.5,         # Regular (400)
    "annotation": 12,      # Regular (400)
    "caption": 12,         # Regular (400)
}

RADIUS = {
    "panel": 12,
    "control": 7,
    "pill": 12,
}

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
}


def get_mono_font_name() -> str:
    """Return the detected best monospace font family for custom painter calls."""
    try:
        families = set(QFontDatabase().families())
        for f in ("Menlo", "Consolas", "Courier New"):
            if f in families:
                return f
    except Exception:
        pass
    return "Menlo" if sys.platform == "darwin" else "Consolas"


def get_ui_font(size_px: int = 14, weight: int = 400) -> QFont:
    """Convenience helper to create a correctly weighted Inter UI QFont in pixels."""
    font = QFont(FONT_FAMILY)
    font.setPixelSize(int(round(size_px)))
    if weight >= 700:
        font.setWeight(QFont.Bold)
    elif weight >= 600:
        font.setWeight(63)  # SemiBold
    elif weight >= 500:
        font.setWeight(57)  # Medium
    else:
        font.setWeight(QFont.Normal)
    return font


def get_mono_font(size_px: int = 12, weight: int = 400) -> QFont:
    """Convenience helper to create a monospace QFont in pixels."""
    font = QFont(get_mono_font_name())
    font.setPixelSize(int(round(size_px)))
    if weight >= 700:
        font.setWeight(QFont.Bold)
    elif weight >= 600:
        font.setWeight(63)
    elif weight >= 500:
        font.setWeight(57)
    else:
        font.setWeight(QFont.Normal)
    return font


def set_font_family(family: str) -> None:
    """Set the UI font family selected by the application."""
    global FONT_FAMILY
    FONT_FAMILY = family


def build_stylesheet() -> str:
    """Build the shared stylesheet with a unified, comfortable type scale."""
    c = COLORS
    return f"""
    QWidget {{
        color: {c['text_primary']};
        font-family: "{FONT_FAMILY}", Arial, sans-serif;
        font-size: {TYPOGRAPHY['body']}px;
        font-weight: 400;
    }}
    QMainWindow, #CentralHost {{
        background-color: {c['bg_app']};
    }}
    #AppHeader {{
        background-color: #FFFFFF;
        border-bottom: 1.5px solid #EAE6F8;
    }}
    #AppTitle {{
        font-size: {TYPOGRAPHY['wordmark']}px;
        font-weight: 700;
        color: #0F172A;
    }}
    #AppSubtitle {{
        color: #7A716B;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2.2px;
    }}
    #NavPillBar {{
        background-color: {c['bg_app']};
        border: 1px solid {c['border_soft']};
        border-radius: 10px;
    }}
    #NavTab {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        color: #64748B;
        font-size: {TYPOGRAPHY['nav_label']}px;
        font-weight: 500;
        padding: 7px 10px;
    }}
    #NavTab:hover {{
        background-color: {c['selected_bg']};
        color: #0F172A;
    }}
    #NavTab[selected="true"] {{
        background-color: {c['selected_bg']};
        border-color: #D8D1FF;
        color: {c['accent_gold_pressed']};
        font-weight: 600;
    }}
    #StudioLaunchButton {{
        background-color: {c['accent_gold']};
        border: none;
        border-radius: 10px;
        color: #FFFFFF;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 0.2px;
        min-height: 38px;
        padding: 8px 16px;
    }}
    #StudioLaunchButton:hover {{
        background-color: {c['accent_gold_hover']};
    }}
    #StudioLaunchButton:pressed {{
        background-color: {c['accent_gold_pressed']};
    }}
    #StudioLeaveButton {{
        background-color: transparent;
        border: 1px solid #2A9A8C;
        border-radius: 10px;
        color: #CCFBF1;
        font-size: 13.5px;
        font-weight: 600;
        min-height: 38px;
        padding: 8px 14px;
    }}
    #StudioLeaveButton:hover {{
        background-color: rgba(94, 234, 212, 0.16);
        border-color: #5EEAD4;
        color: #FFFFFF;
    }}
    #StudioModeBar {{
        background-color: #10131A;
        border: 1px solid #1F2A32;
        border-radius: 10px;
    }}
    #StudioModeChip {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        color: #94A3B8;
        font-size: 13px;
        font-weight: 600;
        min-height: 30px;
        padding: 6px 12px;
    }}
    #StudioModeChip:hover {{
        color: #E2E8F0;
        background-color: rgba(94, 234, 212, 0.08);
    }}
    #StudioModeChip[selected="true"] {{
        background-color: #5EEAD4;
        color: #07080D;
    }}
    #AppHeader[studio="true"] {{
        background-color: #07080D;
        border-bottom: 1px solid #1A1D27;
    }}
    #AppHeader[studio="true"] #AppSubtitle {{
        color: #5EEAD4;
        letter-spacing: 2px;
    }}
    #StatusBar[studio="true"] {{
        background-color: #05060A;
        border-top: 1px solid #1A1D27;
        color: #64748B;
    }}
    #StudioHost, #StudioStage {{
        background-color: #07080D;
        border: none;
    }}
    #StudioViewport {{
        background-color: #0A0C12;
        border: 1px solid #1F2A32;
        border-radius: 16px;
    }}
    #StudioHint {{
        color: #5EEAD4;
        font-size: 12px;
        font-weight: 600;
    }}
    #StudioToolRail, #StudioMatrixHud, #StudioActionBar {{
        background-color: rgba(10, 12, 18, 0.92);
        border: 1px solid rgba(94, 234, 212, 0.18);
        border-radius: 18px;
    }}
    #StudioIconBtn {{
        background-color: transparent;
        border: none;
        border-radius: 11px;
        color: #CBD5E1;
    }}
    #StudioIconBtn:hover {{
        background-color: rgba(94, 234, 212, 0.12);
    }}
    #StudioIconBtn:checked {{
        background-color: #5EEAD4;
    }}
    #StudioActionBtn {{
        background-color: transparent;
        border: none;
        border-radius: 9px;
        color: #E2E8F0;
        font-size: 13px;
        font-weight: 600;
        padding: 0 14px;
        min-height: 34px;
    }}
    #StudioActionBtn:hover {{
        background-color: rgba(94, 234, 212, 22);
        color: #5EEAD4;
    }}
    #StudioActionBtn:checked {{
        background-color: #5EEAD4;
        color: #07080D;
    }}
    #StudioHudKicker {{
        color: #5EEAD4;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.8px;
    }}
    #StudioHudName {{
        color: #F8FAFC;
        font-size: 15px;
        font-weight: 600;
    }}
    #StudioHudMatrix {{
        color: #CBD5E1;
        font-family: {FONT_FAMILY_MONO};
        font-size: 12px;
        font-weight: 500;
    }}
    #StudioHudMeta {{
        color: #64748B;
        font-size: 12px;
        font-weight: 500;
    }}
    #StudioFilmstrip {{
        background-color: #07080D;
        border: none;
    }}
    QDoubleSpinBox#ParamInput {{
        background-color: {c['bg_input']};
        border: 1px solid {c['border']};
        border-radius: {RADIUS['control']}px;
        color: {c['text_primary']};
        font-size: {TYPOGRAPHY['input']}px;
        padding: 3px 6px;
        min-height: 28px;
    }}
    QDoubleSpinBox#ParamInput:focus {{
        background-color: #FFFFFF;
        border: 1px solid {c['accent_gold']};
    }}
    #CentralWorkspace {{
        background-color: #FFFFFF;
        border: 1px solid {c['border_workspace']};
        border-radius: 15px;
    }}
    #SidebarPanel {{
        background-color: #FFFFFF;
        border: 1px solid {c['border_sidebar']};
        border-radius: 15px;
    }}
    #ParamPanel {{
        background-color: transparent;
        border: none;
    }}
    #Panel, #EquationPanel {{
        background-color: #FFFFFF;
        border: 1px solid {c['border_sidebar']};
        border-radius: 15px;
    }}
    #CanvasStack {{
        background-color: transparent;
        border: none;
    }}
    #PanelTitle {{
        color: #0F172A;
        font-size: {TYPOGRAPHY['panel_title']}px;
        font-weight: 600;
    }}
    #PanelDivider {{
        background-color: {c['border']};
        max-height: 1px;
        min-height: 1px;
    }}
    #SidebarPanel #PanelTitle {{
        color: #0F172A;
        font-size: {TYPOGRAPHY['panel_title']}px;
        font-weight: 600;
    }}
    #SidebarPanel #PanelDivider {{
        background-color: {c['border']};
    }}
    #TheoremButton {{
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 9px;
        min-height: 48px;
        padding: 0;
        text-align: left;
    }}
    #TheoremIndex {{
        background-color: #F1F5F9;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        color: #64748B;
        font-family: {FONT_FAMILY_MONO};
        font-size: 12px;
        font-weight: 600;
        qproperty-alignment: AlignCenter;
    }}
    #TheoremName {{
        color: #1E293B;
        font-size: {TYPOGRAPHY['nav_label']}px;
        font-weight: 400;
    }}
    #TheoremButton:hover {{
        background-color: {c['selected_bg']};
        border-color: #D8D1FF;
    }}
    #TheoremButton:hover #TheoremName {{
        color: #0F172A;
    }}
    #TheoremButton:hover #TheoremIndex {{
        background-color: #FFFFFF;
        border-color: #C0B6FF;
        color: {c['accent_gold_pressed']};
    }}
    #TheoremButton:pressed {{
        background-color: #DDD7FF;
    }}
    #TheoremButton[selected="true"] {{
        background-color: {c['accent_gold']};
        border-color: {c['accent_gold']};
        color: #FFFFFF;
    }}
    #TheoremButton[selected="true"] #TheoremIndex,
    #TheoremIndex[selected="true"] {{
        background-color: rgba(255, 255, 255, 0.22);
        border: 1px solid rgba(255, 255, 255, 0.35);
        color: #FFFFFF;
        font-weight: 600;
    }}
    #TheoremButton[selected="true"] #TheoremName,
    #TheoremName[selected="true"] {{
        color: #FFFFFF;
        font-weight: 600;
    }}
    #SidebarPanel #TheoremButton {{
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 9px;
    }}
    #SidebarPanel #TheoremButton:hover {{
        background-color: #F8FAFC;
        border-color: #CBD5E1;
    }}
    #SidebarPanel #TheoremButton[selected="true"] {{
        background-color: {c['accent_gold']};
        border-color: {c['accent_gold']};
    }}
    #ParamLabel {{
        color: #1E293B;
        font-size: {TYPOGRAPHY['param_label']}px;
        font-weight: 500;
    }}
    #ParamInput {{
        background-color: {c['bg_input']};
        border: 1px solid {c['border']};
        border-radius: {RADIUS['control']}px;
        color: {c['text_primary']};
        font-size: {TYPOGRAPHY['input']}px;
        font-weight: 400;
        padding: 5px 9px;
        selection-background-color: {c['accent_gold']};
    }}
    #ParamInput:focus {{
        background-color: #FFFFFF;
        border: 1px solid {c['accent_gold']};
    }}
    #ParamInput[invalid="true"] {{
        border: 1px solid {c['danger']};
    }}
    #ParamUnitBadge {{
        color: {c['accent_gold_pressed']};
        font-size: 12px;
        font-weight: 500;
    }}
    #StepperButton {{
        background-color: #FFFFFF;
        border: 1px solid {c['border']};
        border-radius: 6px;
        color: #475569;
        font-size: 14px;
        font-weight: 500;
    }}
    #StepperButton:hover {{
        background-color: {c['selected_bg']};
        border-color: #CFC7FF;
        color: {c['accent_gold_pressed']};
    }}
    #StepperButton:pressed {{
        background-color: #DDD7FF;
    }}
    #PresetSectionTitle {{
        color: #64748B;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    #ArrayCard {{
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
    }}
    #ArrayCardLabel {{
        color: #1E293B;
        font-size: {TYPOGRAPHY['param_label']}px;
        font-weight: 500;
    }}
    #ArrayCountBadge {{
        background-color: {c['selected_bg']};
        border: 1px solid #D8D1FF;
        border-radius: 9px;
        color: {c['accent_gold_pressed']};
        font-family: {FONT_FAMILY_MONO};
        font-size: 12px;
        font-weight: 600;
        padding: 1px 7px;
    }}
    #ArrayCardInput {{
        background-color: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-radius: 6px;
        color: {c['text_primary']};
        font-family: {FONT_FAMILY_MONO};
        font-size: {TYPOGRAPHY['input']}px;
        font-weight: 400;
        padding: 6px 10px;
    }}
    #ArrayCardInput:focus {{
        background-color: #FFFFFF;
        border-color: {c['accent_gold']};
    }}
    #ArrayCardInput[invalid="true"] {{
        background-color: #FFF5F5;
        border-color: {c['danger']};
        color: {c['danger']};
    }}
    #ArrayHintLabel {{
        color: #64748B;
        font-size: 12px;
        font-weight: 400;
    }}
    #PresetChip {{
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 13px;
        color: #334155;
        font-size: {TYPOGRAPHY['preset_chip']}px;
        font-weight: 500;
        min-height: 28px;
        padding: 4px 12px;
        text-align: center;
    }}
    #PresetChip:hover {{
        background-color: {c['selected_bg']};
        border-color: #C0B6FF;
        color: {c['accent_gold_pressed']};
    }}
    #PresetChip[active="true"] {{
        background-color: {c['selected_bg']};
        border-color: #8C7CE6;
        color: {c['accent_gold_pressed']};
        font-weight: 600;
    }}
    #ParamError {{
        background-color: #FFF4F4;
        border: 1px solid #F3CED2;
        border-radius: 6px;
        color: {c['danger']};
        font-size: 12.5px;
        font-weight: 400;
        padding: 5px 8px;
    }}
    #ParamHint {{
        color: #64748B;
        font-size: 12.5px;
        font-weight: 400;
    }}
    #ApplyButton {{
        background-color: {c['accent_gold']};
        border: 1px solid {c['accent_gold']};
        border-radius: 8px;
        color: #FFFFFF;
        font-size: {TYPOGRAPHY['button']}px;
        font-weight: 600;
        min-height: 38px;
        max-height: 38px;
        padding: 0 16px;
    }}
    #ApplyButton:hover {{
        background-color: {c['accent_gold_hover']};
        border-color: {c['accent_gold_hover']};
    }}
    #ApplyButton:pressed {{
        background-color: {c['accent_gold_pressed']};
    }}
    #ApplyButton:disabled {{
        background-color: #E2E8F0;
        border-color: #E2E8F0;
        color: {c['text_muted']};
    }}
    #ResetParamButton {{
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        color: #475569;
        font-size: 13.5px;
        font-weight: 500;
        min-height: 38px;
        max-height: 38px;
        padding: 0 16px;
    }}
    #ResetParamButton:hover {{
        background-color: {c['bg_panel_alt']};
        border-color: #94A3B8;
        color: {c['text_primary']};
    }}
    #ResetParamButton:pressed {{
        background-color: #EDF2F7;
    }}
    #ResetParamButton:disabled {{
        background-color: #F8FAFC;
        border-color: #E2E8F0;
        color: {c['text_muted']};
    }}
    #PlaceholderCanvas {{
        background-color: {c['bg_viewport']};
        border: 1px solid {c['border_soft']};
        border-radius: 9px;
    }}
    #ZoomButton, #GridButton, #FullscreenButton {{
        background-color: #FFFFFF;
        border: 1px solid {c['border']};
        border-radius: 6px;
        color: #475569;
        font-size: {TYPOGRAPHY['toolbar']}px;
        font-weight: 500;
        min-height: 30px;
        max-height: 30px;
        padding: 2px 7px;
    }}
    #ZoomButton:hover, #GridButton:hover, #FullscreenButton:hover {{
        background-color: {c['selected_bg']};
        border-color: #D8D1FF;
        color: {c['accent_gold_pressed']};
    }}
    #GridButton:checked, #FullscreenButton:checked {{
        background-color: {c['selected_bg']};
        border-color: #CFC7FF;
        color: {c['accent_gold_pressed']};
    }}
    #StepBadge {{
        background-color: {c['selected_bg']};
        border-radius: {RADIUS['pill']}px;
        color: {c['accent_gold_pressed']};
        font-size: {TYPOGRAPHY['step_badge']}px;
        font-weight: 600;
        padding: 3px 10px;
    }}
    #StepTitle {{
        color: #0F172A;
        font-size: {TYPOGRAPHY['step_title']}px;
        font-weight: 600;
    }}
    #EquationLabel {{
        color: #0F172A;
        font-family: {FONT_FAMILY_MONO};
        font-size: {TYPOGRAPHY['equation']}px;
        font-weight: 400;
        line-height: 1.45;
    }}
    #ExplanationLabel {{
        color: #475569;
        font-size: {TYPOGRAPHY['body']}px;
        font-weight: 400;
        line-height: 1.45;
    }}
    #ResultLabel {{
        color: {c['success']};
        font-size: 14px;
        font-weight: 600;
    }}
    #TransportBar {{
        background-color: {c['bg_panel']};
        border: 1px solid {c['border_soft']};
        border-radius: 10px;
    }}
    #TransportButton {{
        background-color: {c['bg_panel_alt']};
        border: 1px solid {c['border']};
        border-radius: {RADIUS['control']}px;
        color: #475569;
        font-size: 13px;
        font-weight: 500;
        min-height: 36px;
        max-height: 36px;
        padding: 0 12px;
    }}
    #TransportButton:hover {{
        background-color: {c['selected_bg']};
        border-color: #D8D1FF;
        color: {c['accent_gold_pressed']};
    }}
    #TransportButton:pressed {{
        background-color: #DDD7FF;
    }}
    #TransportButton:disabled {{
        background-color: {c['bg_panel_alt']};
        border-color: {c['border_soft']};
        color: {c['text_muted']};
    }}
    #TransportButton[primary="true"] {{
        background-color: {c['accent_gold']};
        border-color: {c['accent_gold']};
        color: #FFFFFF;
        font-size: {TYPOGRAPHY['button']}px;
        font-weight: 600;
        min-width: 90px;
    }}
    #TransportButton[primary="true"]:hover {{
        background-color: {c['accent_gold_hover']};
        border-color: {c['accent_gold_hover']};
    }}
    #TransportButton[primary="true"]:pressed {{
        background-color: {c['accent_gold_pressed']};
    }}
    #SpeedLabel {{
        color: #64748B;
        font-size: 12px;
        font-weight: 600;
    }}
    #SpeedBadge {{
        background-color: {c['bg_panel_alt']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        color: {c['accent_gold_pressed']};
        font-family: {FONT_FAMILY_MONO};
        font-size: 12.5px;
        font-weight: 600;
        padding: 2px 6px;
    }}
    #TimelineContainer {{
        background-color: {c['bg_panel_alt']};
        border: 1px solid {c['border_soft']};
        border-radius: 7px;
    }}
    QSlider::groove:horizontal {{
        background: {c['border']};
        border-radius: 2px;
        height: 4px;
    }}
    QSlider::sub-page:horizontal {{
        background: {c['accent_gold']};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {c['accent_gold']};
        border: 2px solid #FFFFFF;
        border-radius: 7px;
        height: 12px;
        margin: -5px 0;
        width: 12px;
    }}
    #StyleCombo {{
        background-color: #FFFFFF;
        border: 1px solid {c['border']};
        border-radius: 6px;
        color: #1E293B;
        font-size: {TYPOGRAPHY['toolbar']}px;
        font-weight: 600;
        min-height: 30px;
        max-height: 30px;
        padding: 2px 8px;
    }}
    #StyleCombo:hover {{
        border-color: #D8D1FF;
        background-color: {c['selected_bg']};
    }}
    #MotionToggle {{
        background-color: #FFFFFF;
        border: 1px solid {c['border']};
        border-radius: 6px;
        color: #475569;
        font-size: {TYPOGRAPHY['toolbar']}px;
        font-weight: 500;
        min-height: 30px;
        max-height: 30px;
        padding: 2px 8px;
    }}
    #MotionToggle:checked {{
        background-color: #FEF3C7;
        border-color: #F59E0B;
        color: #92400E;
    }}
    QComboBox QAbstractItemView {{
        background-color: #FFFFFF;
        border: 1px solid {c['border']};
        selection-background-color: {c['selected_bg']};
        selection-color: {c['text_primary']};
    }}
    #StatusBar {{
        background-color: {c['bg_panel']};
        border-top: 1px solid {c['border']};
        color: #64748B;
        font-size: 12.5px;
        font-weight: 400;
        padding: 3px 12px;
    }}
    #StatusDot {{
        background-color: {c['success']};
        border-radius: 4px;
        max-height: 8px;
        max-width: 8px;
        min-height: 8px;
        min-width: 8px;
    }}
    QScrollBar:vertical {{
        background: transparent;
        margin: 0;
        width: 8px;
    }}
    QScrollBar::handle:vertical {{
        background: #D9DEEA;
        border-radius: 4px;
        min-height: 24px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QToolTip {{
        background-color: #FFFFFF;
        border: 1px solid {c['border']};
        color: {c['text_primary']};
        padding: 4px 7px;
    }}
    #HomeHost {{
        background: transparent;
    }}
    #HomeHeading {{
        color: {c['text_primary']};
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.6px;
    }}
    #HomeSubheading {{
        color: {c['text_muted']};
        font-size: 15px;
        font-weight: 400;
        max-width: 720px;
    }}
    #HomeScroll {{
        background: transparent;
        border: none;
    }}
    #CatalogGridHost {{
        background: transparent;
    }}
    #HomeBackButton {{
        background-color: {c['bg_app']};
        border: 1px solid {c['border_soft']};
        border-radius: 10px;
        color: {c['text_secondary']};
        font-size: 13.5px;
        font-weight: 600;
        min-height: 36px;
        padding: 6px 12px;
    }}
    #HomeBackButton:hover {{
        background-color: {c['selected_bg']};
        color: {c['text_primary']};
    }}
    #LessonModuleChip {{
        background-color: {c['selected_bg']};
        border: 1px solid #D8D1FF;
        border-radius: 10px;
        color: {c['accent_gold_pressed']};
        font-size: 13.5px;
        font-weight: 650;
        min-height: 36px;
        padding: 6px 14px;
    }}
    #TopicCard {{
        background-color: #FFFFFF;
        border: 1px solid {c['border_workspace']};
        border-radius: 16px;
    }}
    #TopicCard[hover="true"], #TopicCard[selected="true"] {{
        border-color: #C9BFFF;
    }}
    #TopicCardPreview {{
        background: transparent;
        border-top-left-radius: 16px;
        border-top-right-radius: 16px;
    }}
    #TopicCardBody {{
        background-color: #FFFFFF;
        border-top: 1px solid {c['border_soft']};
        border-bottom-left-radius: 16px;
        border-bottom-right-radius: 16px;
    }}
    #TopicCardTitle {{
        color: {c['text_primary']};
        font-size: 16px;
        font-weight: 700;
    }}
    #TopicCardCaption {{
        color: {c['text_secondary']};
        font-size: 12.5px;
        font-weight: 400;
    }}
    #TopicCardMeta {{
        color: {c['accent_gold']};
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.2px;
        padding-top: 4px;
    }}
    #GatewayTile {{
        background-color: #FFFFFF;
        border: 1px solid {c['border_workspace']};
        border-radius: 20px;
    }}
    #GatewayTile[kind="studio"] {{
        background-color: #0B0D14;
        border: 1px solid #1F2A32;
    }}
    #GatewayPreview {{
        border-top-left-radius: 20px;
        border-top-right-radius: 20px;
    }}
    #GatewayBody {{
        background-color: #FFFFFF;
        border-top: 1px solid {c['border_soft']};
        border-bottom-left-radius: 20px;
        border-bottom-right-radius: 20px;
    }}
    #GatewayTile[kind="studio"] #GatewayBody {{
        background-color: #0B0D14;
        border-top: 1px solid #1F2A32;
    }}
    #GatewayEyebrow {{
        color: {c['accent_gold']};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.6px;
    }}
    #GatewayTitle {{
        color: {c['text_primary']};
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
    }}
    #GatewayCaption {{
        color: {c['text_secondary']};
        font-size: 14px;
        font-weight: 400;
    }}
    #GatewayTile[kind="studio"] #GatewayEyebrow {{
        color: #5EEAD4;
    }}
    #GatewayTile[kind="studio"] #GatewayTitle {{
        color: #F8FAFC;
    }}
    #GatewayTile[kind="studio"] #GatewayCaption {{
        color: #94A3B8;
    }}
    """
