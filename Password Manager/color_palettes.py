DARK_PALETTE = {
	"bg": "#141414",
	"surface": "#1c1c1c",
	"surface2": "#2a2a2a",
	"accent": "#2ecc71",
	"accent_hover": "#25a35c",
	"btn_secondary": "#494747",
	"btn_auth": "#fb923c",
	"btn_auth_hover" : "#ea7b21",
	"error": "#ef4444",
	"success": "#2ecc71",
	"warning": "#fdcb6e",
	"text": "#e8e8e8",
	"text_dim": "#8a8a8a",
	"placeholder": "#555555",
	"input_bg": "#1e1e1e",
	"input_border": "#3a3a3a",
	"divider": "#2a2a2a",
	"selected_row": "#1e2e1e",
	"disabled_bg": "#222222",
	"disabled_text": "#555555",
}

LIGHT_PALETTE = {
	"bg": "#f8f8f6",
	"surface": "#ffffff",
	"surface2": "#ececec",
	"accent": "#27ae60",
	"accent_hover": "#1f8c4d",
	"btn_secondary": "#2a2a2a",
	"btn_auth": "#c0792a",
	"btn_auth_hover" : "#b86c16",
	"error": "#ef4444",
	"success": "#27ae60",
	"warning": "#fdcb6e",
	"text": "#1a1a1a",
	"text_dim": "#6b6b68",
	"placeholder": "#999999",
	"input_bg": "#ffffff",
	"input_border": "#d0d0d0",
	"divider": "#e4e4e0",
	"selected_row": "#e8f5e8",
	"disabled_bg": "#dddddd",
	"disabled_text": "#999999",
}


def palette_color(key):
	return (LIGHT_PALETTE[key], DARK_PALETTE[key])