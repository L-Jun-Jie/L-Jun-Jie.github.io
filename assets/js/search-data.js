// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "about",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-publications",
          title: "Publications",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "nav-projects",
          title: "Projects",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/projects/";
          },
        },{id: "nav-cv",
          title: "CV",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/cv/";
          },
        },{id: "news-started-my-m-sc-in-software-engineering-at-jilin-university-joining-associate-prof-yong-lai-s-group-to-work-on-constraint-solving-and-smt",
          title: 'Started my M.Sc. in Software Engineering at Jilin University, joining Associate Prof. Yong...',
          description: "",
          section: "News",},{id: "news-paper-accepted-at-tacas-2026-smt-lia-sampling-with-high-diversity-joint-work-with-associate-prof-yong-lai-and-prof-chuan-luo",
          title: 'Paper accepted at TACAS 2026: SMT(LIA) Sampling with High Diversity — joint work...',
          description: "",
          section: "News",},{id: "news-excited-to-share-that-i-have-been-admitted-as-a-ph-d-student-at-hunan-university-starting-september-2026-advised-by-prof-yufeng-zhang-looking-forward-to-the-next-chapter",
          title: 'Excited to share that I have been admitted as a Ph.D. student at...',
          description: "",
          section: "News",},{id: "projects-eda-sampling",
          title: 'EDA Sampling',
          description: "A BDD-based sampling tool for SystemVerilog constraints.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/eda_sampling/";
            },},{id: "projects-highdiv",
          title: 'HighDiv',
          description: "An SMT(LIA) sampler for high-diversity solutions.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/highdiv/";
            },},{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%6A%75%6E%6A%69%65%6C%69%32%30%32%36@%67%6D%61%69%6C.%63%6F%6D", "_blank");
        },
      },{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com/L-Jun-Jie", "_blank");
        },
      },{
        id: 'social-scholar',
        title: 'Google Scholar',
        section: 'Socials',
        handler: () => {
          window.open("https://scholar.google.com/citations?user=O5yFs3gAAAAJ", "_blank");
        },
      },{
        id: 'social-orcid',
        title: 'ORCID',
        section: 'Socials',
        handler: () => {
          window.open("https://orcid.org/0009-0005-3751-9281", "_blank");
        },
      },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
