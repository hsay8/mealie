export interface ThemeConfig {
  lightPrimary: string;
  lightAccent: string;
  lightSecondary: string;
  lightSuccess: string;
  lightInfo: string;
  lightWarning: string;
  lightError: string;
  darkPrimary: string;
  darkAccent: string;
  darkSecondary: string;
  darkSuccess: string;
  darkInfo: string;
  darkWarning: string;
  darkError: string;
}

let __cachedTheme: ThemeConfig | undefined;

async function fetchTheme(): Promise<ThemeConfig | undefined> {
  const route = "/api/app/about/theme";

  try {
    // Fork: the API marks the theme cacheable for a week, so revalidate or a theme change takes a week to show
    const response = await fetch(route, { cache: "no-cache" });
    const data = await response.json();
    return data as ThemeConfig;
  }
  catch {
    return undefined;
  }
}

export default defineNuxtPlugin(async (nuxtApp) => {
  nuxtApp.hook("vuetify:before-create", async ({ vuetifyOptions }) => {
    let theme = __cachedTheme;
    if (!theme) {
      theme = await fetchTheme();
      __cachedTheme = theme;
    }
    vuetifyOptions.theme = {
      defaultTheme: nuxtApp.$config.public.useDark ? "dark" : "light",
      variations: {
        colors: ["primary", "accent", "secondary", "success", "info", "warning", "error", "background"],
        lighten: 3,
        darken: 3,
      },
      themes: {
        light: {
          dark: false,
          colors: {
            primary: theme?.lightPrimary ?? "#0D9488",
            accent: theme?.lightAccent ?? "#6366F1",
            secondary: theme?.lightSecondary ?? "#E11D48",
            success: theme?.lightSuccess ?? "#16A34A",
            info: theme?.lightInfo ?? "#2563EB",
            warning: theme?.lightWarning ?? "#D97706",
            error: theme?.lightError ?? "#DC2626",
            background: "#F3F6FA",
          },
        },
        dark: {
          dark: true,
          colors: {
            primary: theme?.darkPrimary ?? "#2DD4BF",
            accent: theme?.darkAccent ?? "#818CF8",
            secondary: theme?.darkSecondary ?? "#FB7185",
            success: theme?.darkSuccess ?? "#4ADE80",
            info: theme?.darkInfo ?? "#60A5FA",
            warning: theme?.darkWarning ?? "#FBBF24",
            error: theme?.darkError ?? "#F87171",
            background: "#0B1120",
            surface: "#162032",
          },
        },
      },
    };
  });
});
