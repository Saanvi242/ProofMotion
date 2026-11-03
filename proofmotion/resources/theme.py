"""Shared ProofMotion colors, typography, and Qt stylesheet."""

import os
import sys
from PyQt5.QtGui import QFont, QFontDatabase

RESOURCES_DIR = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
CHEVRON_TEAL_PATH = os.path.join(RESOURCES_DIR, "chevron_down_teal.png").replace('\\', '/')
CHEVRON_SLATE_PATH = os.path.join(RESOURCES_DIR, "chevron_down_slate.png").replace('\\', '/')
CHEVRON_WHITE_PATH = os.path.join(RESOURCES_DIR, "chevron_down_white.png").replace('\\', '/')

COLORS = {
    "bg_app": "#F0F1F8",
    "bg_panel": "#FFFFFF",
    "bg_panel_alt": "#F5F6FC",
    "bg_input": "#F3F4FB",
    "bg_viewport": "#F5F6FC",
    "border_workspace": "#D5DDED",
    "border_canvas": "#E0E6F2",
    "border_sidebar": "#DDE2EF",
    "border": "#DCE1ED",
    "border_soft": "#EAECF4",
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
    "panel": 18,
    "control": 10,
    "pill": 14,
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
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #FFFFFF, stop:1 #FAFBFF);
        border-bottom: 1.5px solid #E8E3F8;
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
        border-radius: 14px;
    }}
    #NavTab {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 12px;
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
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #7C6CF0, stop:1 #5B48D0);
        border: none;
        border-radius: 14px;
        color: #FFFFFF;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 0.2px;
        min-height: 40px;
        padding: 8px 20px;
    }}
    #StudioLaunchButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #6E5CE5, stop:1 #4D3BB8);
    }}
    #StudioLaunchButton:pressed {{
        background-color: {c['accent_gold_pressed']};
    }}
    #StudioLeaveButton {{
        background-color: transparent;
        border: 1.5px solid #2A9A8C;
        border-radius: 14px;
        color: #CCFBF1;
        font-size: 13.5px;
        font-weight: 600;
        min-height: 40px;
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
        border-radius: 14px;
    }}
    #StudioModeChip {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 10px;
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
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #07080D, stop:1 #0D0F18);
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
        border-radius: 20px;
    }}
    #StudioHint {{
        color: #5EEAD4;
        font-size: 12px;
        font-weight: 600;
    }}
    #StudioToolRail, #StudioMatrixHud, #StudioActionBar {{
        background-color: rgba(10, 12, 18, 0.92);
        border: 1px solid rgba(94, 234, 212, 0.18);
        border-radius: 20px;
    }}
    #StudioIconBtn {{
        background-color: transparent;
        border: none;
        border-radius: 12px;
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
        border-radius: 12px;
        color: #E2E8F0;
        font-size: 13px;
        font-weight: 600;
        padding: 0 14px;
        min-height: 34px;
    }}
    #StudioActionBtn:hover {{
        background-color: rgba(94, 234, 212, 0.16);
        color: #5EEAD4;
    }}
    #StudioActionBtn:checked {{
        background-color: #5EEAD4;
        color: #07080D;
    }}
    #StudioTopBar, #StudioShapeBar {{
        background-color: rgba(10, 12, 18, 0.94);
        border: 1px solid rgba(94, 234, 212, 0.22);
        border-radius: 16px;
    }}
    #StudioShapePicker,
    #StudioShapeBar QComboBox,
    #StudioStage QComboBox,
    #StudioHost QComboBox,
    [studio="true"] QComboBox {{
        background-color: #121624;
        border: 1.5px solid rgba(94, 234, 212, 0.32);
        border-radius: 10px;
        color: #F8FAFC;
        font-size: 13.5px;
        font-weight: 600;
        padding: 4px 34px 4px 14px;
        min-height: 32px;
    }}
    #StudioShapePicker:hover,
    #StudioShapeBar QComboBox:hover,
    #StudioStage QComboBox:hover,
    #StudioHost QComboBox:hover,
    [studio="true"] QComboBox:hover {{
        border-color: #5EEAD4;
        background-color: #182032;
        color: #5EEAD4;
    }}
    #StudioShapePicker:focus,
    #StudioShapePicker:on,
    #StudioShapeBar QComboBox:focus,
    #StudioShapeBar QComboBox:on,
    #StudioStage QComboBox:focus,
    #StudioStage QComboBox:on,
    #StudioHost QComboBox:focus,
    #StudioHost QComboBox:on {{
        border-color: #5EEAD4;
        background-color: #151A2B;
        color: #FFFFFF;
    }}
    #StudioShapePicker::drop-down,
    #StudioShapeBar QComboBox::drop-down,
    #StudioStage QComboBox::drop-down,
    #StudioHost QComboBox::drop-down,
    [studio="true"] QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 28px;
        border-left: none;
    }}
    #StudioShapePicker::down-arrow,
    #StudioShapeBar QComboBox::down-arrow,
    #StudioStage QComboBox::down-arrow,
    #StudioHost QComboBox::down-arrow,
    [studio="true"] QComboBox::down-arrow {{
        image: url("{CHEVRON_TEAL_PATH}");
        width: 12px;
        height: 12px;
        margin-right: 10px;
    }}
    #StudioShapePicker QAbstractItemView,
    #StudioShapeBar QComboBox QAbstractItemView,
    #StudioStage QComboBox QAbstractItemView,
    #StudioHost QComboBox QAbstractItemView,
    [studio="true"] QComboBox QAbstractItemView {{
        background-color: #0E121E;
        border: 1.5px solid rgba(94, 234, 212, 0.35);
        border-radius: 10px;
        color: #F1F5F9;
        outline: none;
        padding: 6px;
        selection-background-color: rgba(94, 234, 212, 0.22);
        selection-color: #5EEAD4;
    }}
    #StudioShapePicker QAbstractItemView::item,
    #StudioShapeBar QComboBox QAbstractItemView::item,
    #StudioStage QComboBox QAbstractItemView::item,
    #StudioHost QComboBox QAbstractItemView::item,
    [studio="true"] QComboBox QAbstractItemView::item {{
        min-height: 28px;
        padding: 5px 12px;
        border-radius: 6px;
        color: #E2E8F0;
    }}
    #StudioShapePicker QAbstractItemView::item:hover,
    #StudioShapeBar QComboBox QAbstractItemView::item:hover,
    #StudioStage QComboBox QAbstractItemView::item:hover,
    #StudioHost QComboBox QAbstractItemView::item:hover,
    [studio="true"] QComboBox QAbstractItemView::item:hover {{
        background-color: rgba(94, 234, 212, 0.15);
        color: #5EEAD4;
    }}
    #StudioShapePicker QAbstractItemView::item:selected,
    #StudioShapeBar QComboBox QAbstractItemView::item:selected,
    #StudioStage QComboBox QAbstractItemView::item:selected,
    #StudioHost QComboBox QAbstractItemView::item:selected,
    [studio="true"] QComboBox QAbstractItemView::item:selected {{
        background-color: rgba(94, 234, 212, 0.25);
        color: #5EEAD4;
        font-weight: 600;
    }}
    #StudioShapeChip {{
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(94, 234, 212, 0.16);
        border-radius: 8px;
        color: #94A3B8;
        font-size: 12px;
        font-weight: 500;
        padding: 5px 12px;
        min-height: 24px;
    }}
    #StudioShapeChip:hover {{
        background-color: rgba(94, 234, 212, 0.12);
        border-color: rgba(94, 234, 212, 0.4);
        color: #F8FAFC;
    }}
    #StudioShapeChip:checked, #StudioShapeChip[selected="true"] {{
        background-color: #5EEAD4;
        border-color: #5EEAD4;
        color: #07080D;
        font-weight: 700;
    }}
    #StudioPipelineBadge {{
        background-color: rgba(94, 234, 212, 0.08);
        border: 1px solid rgba(94, 234, 212, 0.2);
        border-radius: 8px;
        color: #5EEAD4;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.6px;
        padding: 5px 12px;
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
        border: 1.5px solid {c['border']};
        border-radius: {RADIUS['control']}px;
        color: {c['text_primary']};
        font-size: {TYPOGRAPHY['input']}px;
        padding: 3px 6px;
        min-height: 28px;
    }}
    QDoubleSpinBox#ParamInput:focus {{
        background-color: #FFFFFF;
        border: 1.5px solid {c['accent_gold']};
    }}
    #CentralWorkspace {{
        background-color: #FFFFFF;
        border: 1px solid {c['border_workspace']};
        border-radius: {RADIUS['panel']}px;
    }}
    #SidebarPanel {{
        background-color: #FFFFFF;
        border: 1px solid {c['border_sidebar']};
        border-radius: {RADIUS['panel']}px;
    }}
    #ParamPanel {{
        background-color: transparent;
        border: none;
    }}
    #Panel, #EquationPanel {{
        background-color: #FFFFFF;
        border: 1px solid {c['border_sidebar']};
        border-radius: {RADIUS['panel']}px;
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
        border: 1.5px solid #E8ECF5;
        border-radius: 12px;
        min-height: 48px;
        padding: 0;
        text-align: left;
    }}
    #TheoremIndex {{
        background-color: #F1F5F9;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
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
        border-color: #D0C7FF;
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
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #7C6CF0, stop:1 #5B48D0);
        border-color: transparent;
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
        border: 1.5px solid #E8ECF5;
        border-radius: 12px;
    }}
    #SidebarPanel #TheoremButton:hover {{
        background-color: #F5F3FF;
        border-color: #D0C7FF;
    }}
    #SidebarPanel #TheoremButton[selected="true"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #7C6CF0, stop:1 #5B48D0);
        border-color: transparent;
    }}
    #ParamLabel {{
        color: #1E293B;
        font-size: {TYPOGRAPHY['param_label']}px;
        font-weight: 500;
    }}
    #ParamInput {{
        background-color: {c['bg_input']};
        border: 1.5px solid {c['border']};
        border-radius: {RADIUS['control']}px;
        color: {c['text_primary']};
        font-size: {TYPOGRAPHY['input']}px;
        font-weight: 400;
        padding: 5px 9px;
        selection-background-color: {c['accent_gold']};
    }}
    #ParamInput:focus {{
        background-color: #FFFFFF;
        border: 1.5px solid {c['accent_gold']};
    }}
    #ParamInput[invalid="true"] {{
        border: 1.5px solid {c['danger']};
    }}
    #ParamUnitBadge {{
        color: {c['accent_gold_pressed']};
        font-size: 12px;
        font-weight: 500;
    }}
    #StepperButton {{
        background-color: #FFFFFF;
        border: 1.5px solid {c['border']};
        border-radius: 8px;
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
        border: 1.5px solid #E8ECF5;
        border-radius: 12px;
    }}
    #ArrayCardLabel {{
        color: #1E293B;
        font-size: {TYPOGRAPHY['param_label']}px;
        font-weight: 500;
    }}
    #ArrayCountBadge {{
        background-color: {c['selected_bg']};
        border: 1px solid #D8D1FF;
        border-radius: 10px;
        color: {c['accent_gold_pressed']};
        font-family: {FONT_FAMILY_MONO};
        font-size: 12px;
        font-weight: 600;
        padding: 1px 7px;
    }}
    #ArrayCardInput {{
        background-color: #F8FAFC;
        border: 1.5px solid #CBD5E1;
        border-radius: 8px;
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
        border: 1.5px solid #E8ECF5;
        border-radius: 16px;
        color: #334155;
        font-size: {TYPOGRAPHY['preset_chip']}px;
        font-weight: 500;
        min-height: 30px;
        padding: 5px 14px;
        text-align: center;
    }}
    #PresetChip:hover {{
        background-color: {c['selected_bg']};
        border-color: #C0B6FF;
        color: {c['accent_gold_pressed']};
    }}
    #PresetChip[active="true"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #EDE8FF, stop:1 #E0D9FF);
        border-color: #8C7CE6;
        color: {c['accent_gold_pressed']};
        font-weight: 600;
    }}
    #ParamError {{
        background-color: #FFF4F4;
        border: 1px solid #F3CED2;
        border-radius: 10px;
        color: {c['danger']};
        font-size: 12.5px;
        font-weight: 400;
        padding: 6px 10px;
    }}
    #ParamHint {{
        color: #64748B;
        font-size: 12.5px;
        font-weight: 400;
    }}
    #ApplyButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #7C6CF0, stop:1 #5B48D0);
        border: none;
        border-radius: 12px;
        color: #FFFFFF;
        font-size: {TYPOGRAPHY['button']}px;
        font-weight: 600;
        min-height: 40px;
        max-height: 40px;
        padding: 0 18px;
    }}
    #ApplyButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #6E5CE5, stop:1 #4D3BB8);
    }}
    #ApplyButton:pressed {{
        background-color: {c['accent_gold_pressed']};
    }}
    #ApplyButton:disabled {{
        background-color: #E2E8F0;
        border: none;
        color: {c['text_muted']};
    }}
    #ResetParamButton {{
        background-color: #FFFFFF;
        border: 1.5px solid #D0D5E1;
        border-radius: 12px;
        color: #475569;
        font-size: 13.5px;
        font-weight: 500;
        min-height: 40px;
        max-height: 40px;
        padding: 0 18px;
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
        border-radius: 14px;
    }}
    #ZoomButton, #GridButton, #FullscreenButton {{
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        color: #64748B;
        font-size: 12px;
        font-weight: 500;
        min-height: 28px;
        max-height: 28px;
        padding: 2px 9px;
    }}
    #ZoomButton:hover, #GridButton:hover, #FullscreenButton:hover {{
        background-color: #F1F5F9;
        border-color: #CBD5E1;
        color: #1E293B;
    }}
    #GridButton:checked, #FullscreenButton:checked {{
        background-color: #EDE9FE;
        border-color: #DDD6FE;
        color: #6C5CE7;
        font-weight: 600;
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
        border-radius: 14px;
    }}
    #TransportButton {{
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 6px;
        color: #475569;
        font-size: 13px;
        font-weight: 500;
        min-height: 32px;
        max-height: 32px;
        padding: 0 10px;
    }}
    #TransportButton:hover {{
        background-color: #F1F5F9;
        border-color: #E2E8F0;
        color: #0F172A;
    }}
    #TransportButton:pressed {{
        background-color: #E2E8F0;
    }}
    #TransportButton:disabled {{
        background-color: transparent;
        border-color: transparent;
        color: #CBD5E1;
    }}
    #TransportButton[primary="true"] {{
        background-color: #6C5CE7;
        border: 1px solid #5B48D0;
        border-radius: 7px;
        color: #FFFFFF;
        font-size: 13px;
        font-weight: 700;
        min-width: 96px;
        min-height: 32px;
        max-height: 32px;
    }}
    #TransportButton[primary="true"]:hover {{
        background-color: #5B48D0;
        border-color: #4D3BB8;
    }}
    #TransportButton[primary="true"]:pressed {{
        background-color: #4D3BB8;
    }}
    #SpeedLabel {{
        color: #64748B;
        font-size: 12px;
        font-weight: 600;
    }}
    #SpeedBadge {{
        background-color: {c['bg_panel_alt']};
        border: 1.5px solid {c['border']};
        border-radius: 8px;
        color: {c['accent_gold_pressed']};
        font-family: {FONT_FAMILY_MONO};
        font-size: 12.5px;
        font-weight: 600;
        padding: 2px 6px;
    }}
    #TimelineContainer {{
        background-color: {c['bg_panel_alt']};
        border: 1px solid {c['border_soft']};
        border-radius: 10px;
    }}
    QSlider::groove:horizontal {{
        background: {c['border']};
        border-radius: 3px;
        height: 5px;
    }}
    QSlider::sub-page:horizontal {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #8B78F2, stop:1 #6C5CE7);
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: #FFFFFF;
        border: 2.5px solid {c['accent_gold']};
        border-radius: 8px;
        height: 14px;
        margin: -5px 0;
        width: 14px;
    }}
    QComboBox {{
        background-color: #FFFFFF;
        border: 1.5px solid {c['border']};
        border-radius: 8px;
        color: {c['text_primary']};
        font-size: {TYPOGRAPHY['input']}px;
        font-weight: 500;
        padding: 4px 30px 4px 10px;
        min-height: 30px;
    }}
    QComboBox:hover {{
        border-color: #C0B6FF;
        background-color: #FAFAFE;
    }}
    QComboBox:focus, QComboBox:on {{
        border-color: {c['accent_gold']};
        background-color: #FFFFFF;
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 26px;
        border-left: none;
    }}
    QComboBox::down-arrow {{
        image: url("{CHEVRON_SLATE_PATH}");
        width: 11px;
        height: 11px;
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: #FFFFFF;
        border: 1.5px solid {c['border']};
        border-radius: 8px;
        color: {c['text_primary']};
        selection-background-color: {c['selected_bg']};
        selection-color: {c['accent_gold_pressed']};
        outline: none;
        padding: 4px;
    }}
    QComboBox QAbstractItemView::item {{
        min-height: 26px;
        padding: 4px 8px;
        border-radius: 4px;
        color: {c['text_primary']};
    }}
    QComboBox QAbstractItemView::item:hover {{
        background-color: {c['selected_bg']};
        color: {c['text_primary']};
    }}
    QComboBox QAbstractItemView::item:selected {{
        background-color: {c['selected_bg']};
        color: {c['accent_gold_pressed']};
        font-weight: 600;
    }}
    #StyleCombo {{
        background-color: #FFFFFF;
        border: 1.5px solid {c['border']};
        border-radius: 8px;
        color: #1E293B;
        font-size: {TYPOGRAPHY['toolbar']}px;
        font-weight: 600;
        min-height: 30px;
        max-height: 30px;
        padding: 2px 26px 2px 8px;
    }}
    #StyleCombo:hover {{
        border-color: #D8D1FF;
        background-color: {c['selected_bg']};
    }}
    #StyleCombo::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 24px;
        border-left: none;
    }}
    #StyleCombo::down-arrow {{
        image: url("{CHEVRON_SLATE_PATH}");
        width: 10px;
        height: 10px;
        margin-right: 6px;
    }}
    [studio="true"] #StyleCombo, #StudioHost #StyleCombo, #StudioStage #StyleCombo {{
        background-color: #121624;
        border: 1.5px solid rgba(94, 234, 212, 0.28);
        color: #F8FAFC;
    }}
    [studio="true"] #StyleCombo::down-arrow, #StudioHost #StyleCombo::down-arrow, #StudioStage #StyleCombo::down-arrow {{
        image: url("{CHEVRON_TEAL_PATH}");
    }}
    #MotionToggle {{
        background-color: #FFFFFF;
        border: 1.5px solid {c['border']};
        border-radius: 8px;
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
    #StatusBar {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #FFFFFF, stop:1 #FAFBFF);
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
        font-size: 30px;
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
        background-color: rgba(255, 255, 255, 0.85);
        border: 1.5px solid {c['border_soft']};
        border-radius: 14px;
        color: {c['text_secondary']};
        font-size: 13.5px;
        font-weight: 600;
        min-height: 38px;
        padding: 6px 14px;
    }}
    #HomeBackButton:hover {{
        background-color: {c['selected_bg']};
        border-color: #D0C7FF;
        color: {c['text_primary']};
    }}
    #LessonModuleChip {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #EDE8FF, stop:1 #E0D9FF);
        border: 1.5px solid #D0C7FF;
        border-radius: 14px;
        color: {c['accent_gold_pressed']};
        font-size: 13.5px;
        font-weight: 650;
        min-height: 38px;
        padding: 6px 14px;
    }}
    #TopicCard {{
        background-color: transparent;
        border: none;
    }}
    #TopicCardPreview {{
        background-color: transparent;
        border: none;
    }}
    #TopicCardBody {{
        background-color: transparent;
        border: none;
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
        background-color: transparent;
        border: none;
    }}
    #GatewayTile[kind="studio"] {{
        background-color: transparent;
        border: none;
    }}
    #GatewayPreview {{
        background-color: transparent;
        border: none;
    }}
    #GatewayBody {{
        background-color: transparent;
        border: none;
    }}
    #GatewayTile[kind="studio"] #GatewayBody {{
        background-color: transparent;
        border: none;
    }}
    #GatewayEyebrow {{
        color: {c['accent_gold']};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.6px;
    }}
    #GatewayTitle {{
        color: {c['text_primary']};
        font-size: 28px;
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
    #TopicCard[hover="true"] #TopicCardTitle {{
        color: #5B4AD4;
    }}
    #TopicCardArrow {{
        background-color: #F1EDFF;
        border: 1px solid #E0D8FF;
        border-radius: 9px;
        color: #6C5CE7;
        font-size: 13px;
        font-weight: 700;
        padding: 1px 7px;
    }}
    #TopicCard[hover="true"] #TopicCardArrow {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7C6CF0, stop:1 #5B48D0);
        color: #FFFFFF;
        border-color: transparent;
    }}
    #GatewayCtaBadge {{
        background-color: #F1EDFF;
        border: 1px solid #DCD4FF;
        border-radius: 12px;
        color: #5B4AD4;
        font-size: 12.5px;
        font-weight: 650;
        padding: 5px 14px;
    }}
    #GatewayTile[hover="true"] #GatewayCtaBadge {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7C6CF0, stop:1 #5B48D0);
        color: #FFFFFF;
        border-color: transparent;
    }}
    #GatewayTile[kind="studio"] #GatewayCtaBadge {{
        background-color: rgba(94, 234, 212, 0.12);
        border: 1px solid rgba(94, 234, 212, 0.28);
        border-radius: 12px;
        color: #5EEAD4;
        font-size: 12.5px;
        font-weight: 650;
        padding: 5px 14px;
    }}
    #GatewayTile[kind="studio"][hover="true"] #GatewayCtaBadge {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5EEAD4, stop:1 #2DD4BF);
        color: #07080D;
        border-color: transparent;
    }}
    #StudioPanel {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 rgba(16, 21, 32, 0.98), stop:1 rgba(10, 13, 20, 0.98));
        border: 1px solid rgba(94, 234, 212, 0.20);
        border-radius: 18px;
    }}
    #StudioPanel #PanelTitle {{
        color: #F8FAFC;
        font-weight: 700;
    }}
    #StudioPanel #PanelDivider {{
        background-color: rgba(94, 234, 212, 0.18);
    }}
    #StudioPanel #ParamHint {{
        color: #94A3B8;
    }}
    #StudioPanel #EquationLabel {{
        color: #5EEAD4;
        font-family: {FONT_FAMILY_MONO};
    }}
    #StudioPanel #ExplanationLabel {{
        color: #CBD5E1;
    }}
    """
