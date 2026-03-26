from __future__ import annotations

from ui.brand.design_tokens import DesignTokens


def build_stylesheet() -> str:
    return f"""
    QMainWindow, QWidget#appRoot {{
        background: {DesignTokens.bg_primary};
        color: {DesignTokens.text_primary};
        font-family: Segoe UI;
        font-size: 14px;
    }}
    QFrame#sidebar, QFrame#rightPane, QFrame#actionBar, QFrame#onecHostFrame, QWidget#onboardingBubble {{
        background: {DesignTokens.bg_secondary};
        border-radius: {DesignTokens.radius_lg}px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }}
    QPushButton {{
        background: rgba(255, 255, 255, 0.04);
        color: {DesignTokens.text_primary};
        border-radius: {DesignTokens.radius_md}px;
        padding: 10px 14px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }}
    QPushButton:hover {{
        background: {DesignTokens.accent_hover};
        color: #08111f;
    }}
    QPushButton:pressed {{
        background: {DesignTokens.accent_main};
        color: #08111f;
    }}
    QPushButton:checked {{
        background: {DesignTokens.accent_main};
        color: #08111f;
        font-weight: 700;
    }}
    QLabel#sectionTitle, QLabel#hostTitle, QLabel#onboardingTitle {{
        font-size: 22px;
        font-weight: 700;
    }}
    QLabel#sectionSubtitle, QLabel#hostStatus, QLabel#onboardingText {{
        color: {DesignTokens.text_secondary};
    }}
    QLabel#hostInlineMessage {{
        color: {DesignTokens.text_secondary};
        padding: 18px;
    }}
    QWidget#toastMessage {{
        background: rgba(10, 18, 32, 0.95);
        border-radius: {DesignTokens.radius_md}px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }}
    QWidget#toastMessage[kind="success"] {{
        background: rgba(20, 71, 41, 0.96);
        border: 1px solid rgba(92, 214, 129, 0.45);
    }}
    QWidget#toastMessage[kind="error"] {{
        background: rgba(90, 25, 25, 0.96);
        border: 1px solid rgba(255, 107, 107, 0.45);
    }}
    QLabel#toastIcon {{
        font-size: 18px;
        font-weight: 700;
        color: {DesignTokens.text_primary};
    }}
    QLabel#toastText {{
        color: {DesignTokens.text_primary};
    }}
    QListWidget, QLineEdit, QSpinBox, QComboBox, QTextEdit {{
        background: rgba(255, 255, 255, 0.03);
        color: {DesignTokens.text_primary};
        border-radius: {DesignTokens.radius_md}px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 8px;
    }}
    QCheckBox {{
        spacing: 8px;
    }}
    QPushButton#logDrawerToggle {{
        background: {DesignTokens.bg_secondary};
        border-radius: {DesignTokens.radius_md}px;
        padding: 8px 12px;
    }}
    """
