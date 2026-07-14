In_wsl = os.getenv("WSL_DISTRO_NAME") ~= nil
local is_vscode = vim.g.vscode ~= nil

if In_wsl then
	vim.g.clipboard = {
		name = "wsl clipboard",
		copy = {
			["+"] = { "/mnt/c/Windows/system32/clip.exe" },
			["*"] = { "/mnt/c/Windows/system32/clip.exe" },
		},
		paste = {
			["+"] = { "/mnt/c/Program Files/Neovim/bin/win32yank.exe" },
			["*"] = { "/mnt/c/Program Files/Neovim/bin/win32yank.exe" },
		},
		cache_enabled = false,
	}
end

-- Bootstrap lazy.nvim
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
	local lazyrepo = "https://github.com/folke/lazy.nvim.git"
	local out = vim.fn.system({ "git", "clone", "--filter=blob:none", "--branch=stable", lazyrepo, lazypath })
	if vim.v.shell_error ~= 0 then
		vim.api.nvim_echo({
			{ "Failed to clone lazy.nvim:\n", "ErrorMsg" },
			{ out, "WarningMsg" },
			{ "\nPress any key to exit..." },
		}, true, {})
		vim.fn.getchar()
		os.exit(1)
	end
end

vim.opt.rtp:prepend(lazypath)
vim.g.mapleader = " "
vim.g.maplocalleader = "\\"

-- Ensure files end with a final newline when written.
vim.opt.fixendofline = true
vim.opt.endofline = true

-- Use Neovim's built-in spell checker for prose-like filetypes.
-- Project/product words live in spell/en.utf-8.add under the nvim config directory.
vim.opt.spelllang = { "en" }
local spellfile = vim.fn.stdpath("config") .. "/spell/en.utf-8.add"
local spellfile_compiled = spellfile .. ".spl"
vim.opt.spellfile = spellfile
vim.fn.mkdir(vim.fn.fnamemodify(spellfile, ":h"), "p")
if vim.fn.filereadable(spellfile) == 1 then
	local add_mtime = vim.fn.getftime(spellfile)
	local spl_mtime = vim.fn.getftime(spellfile_compiled)
	if spl_mtime < add_mtime then
		vim.cmd("silent! mkspell! " .. vim.fn.fnameescape(spellfile))
	end
end
vim.api.nvim_create_autocmd("FileType", {
	pattern = { "gitcommit", "markdown", "rst", "text" },
	callback = function()
		vim.opt_local.spell = true
	end,
})

local function configure_spell_highlights()
	-- In truecolor terminals Neovim uses GUI highlight attributes, not cterm.
	-- Use a plain underline there too, because many Linux terminals do not render undercurl clearly.
	vim.cmd("highlight SpellBad gui=underline guisp=#f7768e cterm=underline")
	vim.cmd("highlight SpellCap gui=underline guisp=#e0af68 cterm=underline")
	vim.cmd("highlight SpellRare gui=underline guisp=#bb9af7 cterm=underline")
	vim.cmd("highlight SpellLocal gui=underline guisp=#7dcfff cterm=underline")
end

vim.api.nvim_create_autocmd({ "ColorScheme", "VimEnter" }, {
	pattern = "*",
	callback = configure_spell_highlights,
})
configure_spell_highlights()

-- Setup lazy.nvim
require("lazy").setup({
	spec = {
		{ "LazyVim/LazyVim", import = "lazyvim.plugins" },
		{
			"CopilotC-Nvim/CopilotChat.nvim",
			branch = "canary",
			dependencies = {
				{ "github/copilot.vim" },
				{ "nvim-lua/plenary.nvim" },
			},
			opts = {},
		},
		{ "folke/noice.nvim", event = "VeryLazy", opts = {}, dependencies = {} },
		{
			"folke/which-key.nvim",
			opts = {
				spec = {
					{
						"<leader>t",
						group = "tools",
						icon = { icon = "󰒓", color = "cyan" },
					},
					{
						"<leader>a",
						group = "agent",
						icon = { icon = "󰚩", color = "orange" },
					},
				},
			},
		},
		{ "neovim/nvim-lspconfig" },
		{
			"seblyng/roslyn.nvim",
			ft = { "cs", "csproj", "sln" },
			opts = {
				-- Prefer the `roslyn` wrapper if installed.
				exe = function()
					if vim.fn.executable("roslyn") == 1 then
						return { "roslyn" }
					end
					if vim.fn.executable("Microsoft.CodeAnalysis.LanguageServer") == 1 then
						return { "Microsoft.CodeAnalysis.LanguageServer" }
					end
					return nil
				end,
			},
			config = function(_, opts)
				local ok, roslyn = pcall(require, "roslyn")
				if not ok then
					return
				end
				local exe = opts.exe and opts.exe() or nil
				if not exe then
					vim.schedule(function()
						vim.notify(
							"roslyn.nvim: no Roslyn LSP executable found (install `roslyn` or Roslyn Language Server)",
							vim.log.levels.WARN
						)
					end)
					return
				end
				roslyn.setup({
					exe = exe,
				})
			end,
		},
		{ "nvim-treesitter/nvim-treesitter", branch = "main", lazy = false, build = ":TSUpdate" },
		{
			"nvim-lualine/lualine.nvim",
			dependencies = { "nvim-tree/nvim-web-devicons" },
		},
		{ "nvim-telescope/telescope.nvim", tag = "0.1.8" },
		{
			"nvim-neo-tree/neo-tree.nvim",
			branch = "v3.x",
			dependencies = {
				"nvim-lua/plenary.nvim",
				"nvim-tree/nvim-web-devicons", -- not strictly required, but recommended
				"MunifTanjim/nui.nvim",
			},
		},
		{
			"MeanderingProgrammer/render-markdown.nvim",
			opts = {},
			dependencies = { "nvim-treesitter/nvim-treesitter", "nvim-mini/mini.icons" },
		},
		{
			"iamcco/markdown-preview.nvim",
			cmd = { "MarkdownPreviewToggle", "MarkdownPreview", "MarkdownPreviewStop" },
			build = "cd app && yarn install",
			init = function()
				vim.g.mkdp_filetypes = { "markdown" }
			end,
			ft = { "markdown" },
		},
		{
			"ibhagwan/fzf-lua",
			-- optional for icon support
			dependencies = { "nvim-tree/nvim-web-devicons" },
			config = function()
				-- calling `setup` is optional for customization
				require("fzf-lua").setup({ "fzf-tmux", winopts = { preview = { default = "bat" } } })
			end,
		},
		{
			"stevearc/conform.nvim",
			opts = {
				formatters_by_ft = {
					rst = { "rstfmt" },
				},
				formatters = {
					rstfmt = {
						prepend_args = { "-w", "120" },
						condition = function(_, ctx)
							-- rstfmt uses docutils directly and does not load this project's
							-- Sphinx extensions, so it errors on custom directives such as
							-- `.. md-mermaid::`. Skip rstfmt for those files rather than
							-- breaking save-on-format.
							local lines = vim.api.nvim_buf_get_lines(ctx.buf, 0, -1, false)
							for _, line in ipairs(lines) do
								if line:match("^%s*%.%.%s+md%-mermaid::") then
									return false
								end
							end
							return true
						end,
					},
				},
			},
		},
		{
			"pablopunk/pi.nvim",
			opts = {
				provider = "github-copilot",
				model = "gpt-5.5",
				thinking = "low",
			},
		},
	},
	install = { colorscheme = { "tokyonight" } },
	checker = { enabled = true },
})

local custom_tokyonight
if not is_vscode then
	custom_tokyonight = require("lualine.themes.tokyonight")
	custom_tokyonight.normal.c.bg = "#1a1b26"

	require("noice").setup({
		lsp = {
			-- override markdown rendering so that **cmp** and other plugins use **Treesitter**
			override = {
				["vim.lsp.util.convert_input_to_markdown_lines"] = true,
				["vim.lsp.util.stylize_markdown"] = true,
				["cmp.entry.get_documentation"] = true, -- requires hrsh7th/nvim-cmp
			},
		},
		-- you can enable a preset for easier configuration
		presets = {
			bottom_search = true, -- use a classic bottom cmdline for search
			command_palette = true, -- position the cmdline and popupmenu together
			long_message_to_split = true, -- long messages will be sent to a split
			inc_rename = false, -- enables an input dialog for inc-rename.nvim
			lsp_doc_border = false, -- add a border to hover docs and signature help
		},
	})
end

-- format buffer on write
vim.api.nvim_create_autocmd("BufWritePre", {
	pattern = "*",
	callback = function(args)
		require("conform").format({ bufnr = args.buf, async = false })
		vim.bo[args.buf].binary = false
		vim.bo[args.buf].endofline = true
		vim.bo[args.buf].fixendofline = true
		vim.bo[args.buf].fileformat = "unix"
	end,
})

-- format buffer on demand
vim.api.nvim_create_user_command("Format", function(args)
	local range = nil
	if args.count ~= -1 then
		local end_line = vim.api.nvim_buf_get_lines(0, args.line2 - 1, args.line2, true)[1]
		range = {
			start = { args.line1, 0 },
			["end"] = { args.line2, end_line:len() },
		}
	end
	require("conform").format({ async = true, lsp_format = "fallback", range = range })
end, { range = true })

if not is_vscode then
	-- configure status line
	local has_noice, noice = pcall(require, "noice")
	require("lualine").setup({
		options = {
			icons_enabled = true,
			theme = custom_tokyonight,
			component_separators = { left = "", right = "" },
			section_separators = { left = "", right = "" },
			disabled_filetypes = {
				statusline = {},
				winbar = {},
			},
			ignore_focus = {},
			always_divide_middle = true,
			globalstatus = false,
			refresh = {
				statusline = 1000,
				tabline = 1000,
				winbar = 1000,
			},
		},
		sections = {
			lualine_a = { { "mode", separator = { left = "", right = "" }, right_padding = 2 } },
			lualine_b = { "branch", "diff", "diagnostics" },
			lualine_c = { { "filename", separator = { right = "" }, color = { bg = "#292e42" } } },
			lualine_x = {
				{
					function()
						if has_noice and noice.api and noice.api.status and noice.api.status.mode then
							return noice.api.status.mode.get()
						end
						return ""
					end,
					cond = function()
						return has_noice
							and noice.api
							and noice.api.status
							and noice.api.status.mode
							and noice.api.status.mode.has()
					end,
					separator = { left = "" },
					color = { bg = "#7dcfff", fg = "#1f2335" },
				},
				{ "encoding", separator = { left = "" }, color = { bg = "#bb9af7", fg = "#1f2335" } },
				{ "fileformat", separator = { left = "" }, color = { bg = "#9d7cd8", fg = "#1f2335" } },
				{ "filetype", separator = { left = "" }, color = { bg = "#414868", fg = "#ffffff" } },
			},
			lualine_y = { { "progress", color = { bg = "#c53b53", fg = "#ffffff" } } },
			lualine_z = {
				{
					"location",
					separator = { left = "", right = "" },
					color = { bg = "#ff007c", fg = "#ffffff" },
					left_padding = 2,
				},
			},
		},
		inactive_sections = {
			lualine_a = {},
			lualine_b = {},
			lualine_c = { "filename" },
			lualine_x = { "location" },
			lualine_y = {},
			lualine_z = {},
		},
		tabline = {},
		winbar = {},
		inactive_winbar = {},
		extensions = {},
	})

	-- colorscheme options
	require("tokyonight").setup({
		style = "night",
		on_colors = function() end,
		on_highlights = function() end,
	})

	vim.cmd([[colorscheme tokyonight]])
end

-- Disable Mouse
vim.opt.mousescroll = "ver:0,hor:0"
vim.keymap.set("", "<up>", "<nop>", { noremap = true })
vim.keymap.set("", "<down>", "<nop>", { noremap = true })
vim.keymap.set("i", "<up>", "<nop>", { noremap = true })
vim.keymap.set("i", "<down>", "<nop>", { noremap = true })

-- create keybinding for neotree
vim.keymap.set("n", "<C-\\>", "<Cmd>Neotree toggle<CR>")

-- disable mouse
vim.opt.mouse = ""

-- disable relative line numbers
vim.opt.relativenumber = false

-- pi ai
vim.keymap.set("n", "<leader>ai", ":PiAsk<CR>", { desc = "Ask pi" })
vim.keymap.set("v", "<leader>ai", ":PiAskSelection<CR>", { desc = "Ask pi (selection)" })

-- keybindings
vim.keymap.set("n", "<leader>tf", "<cmd>:Format<CR>", { desc = "Format File" })
vim.keymap.set("v", "<leader>tf", ":Format", { desc = "Format Selection" })
