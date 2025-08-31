<html lang="ro"><head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Tablou de Bord — Voice Booking</title>
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&amp;display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  </head>
  <body class="min-h-screen bg-gray-900 text-gray-100 antialiased" style="font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial;">
    <div id="app" class="flex min-h-screen">
      <!-- Sidebar -->
      <aside id="sidebar" class="hidden md:flex md:flex-col md:w-72 md:shrink-0 border-r border-white/10 bg-gray-800/60 backdrop-blur-lg">
        <!-- Logo -->
        <div class="flex items-center gap-3 px-5 h-16 border-b border-white/10">
          <div class="grid place-items-center w-8 h-8 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 tracking-tight text-sm font-semibold">VB</div>
          <div class="flex flex-col">
            <span class="text-sm font-semibold tracking-tight">Voice Booking</span>
            <span class="text-[11px] text-gray-400">Admin Dashboard</span>
          </div>
        </div>

        <!-- Nav -->
        <nav class="flex-1 px-3 py-4 space-y-1">
          <a href="#" class="group flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium bg-gray-700/50 border border-white/10 hover:border-cyan-500/40 hover:bg-gray-700/70 transition-colors">
            <i data-lucide="layout-dashboard" class="w-4.5 h-4.5 text-cyan-400"></i>
            <span>Dashboard</span>
          </a>
          <a href="#" class="group flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-300 hover:text-white hover:bg-gray-700/40 border border-transparent hover:border-white/10 transition-colors">
            <i data-lucide="calendar" class="w-4.5 h-4.5"></i>
            <span>Calendar</span>
          </a>
          <a href="#" class="group flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-300 hover:text-white hover:bg-gray-700/40 border border-transparent hover:border-white/10 transition-colors">
            <i data-lucide="users" class="w-4.5 h-4.5"></i>
            <span>Clienți</span>
          </a>
          <a href="#" class="group flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-300 hover:text-white hover:bg-gray-700/40 border border-transparent hover:border-white/10 transition-colors">
            <i data-lucide="scissors" class="w-4.5 h-4.5"></i>
            <span>Servicii &amp; Prețuri</span>
          </a>
          <a href="#" class="group flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-300 hover:text-white hover:bg-gray-700/40 border border-transparent hover:border-white/10 transition-colors">
            <i data-lucide="chart-line" class="w-4.5 h-4.5"></i>
            <span>Statistici</span>
          </a>
          <a href="#" class="group flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-300 hover:text-white hover:bg-gray-700/40 border border-transparent hover:border-white/10 transition-colors">
            <i data-lucide="mic" class="w-4.5 h-4.5"></i>
            <span>Setări Agent Vocal</span>
          </a>
        </nav>

        <!-- Profile -->
        <div class="mt-auto p-4 border-t border-white/10">
          <div class="flex items-center gap-3">
            <img src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&amp;w=200&amp;auto=format&amp;fit=crop" alt="user" class="w-9 h-9 rounded-md object-cover border border-white/10">
            <div class="flex-1">
              <div class="text-sm font-medium">Alexandra I.</div>
              <div class="text-xs text-gray-400">Owner</div>
            </div>
            <button class="p-2 rounded-md hover:bg-gray-700/50 border border-white/10 hover:border-white/20 transition-colors" title="Logout">
              <i data-lucide="log-out" class="w-4.5 h-4.5"></i>
            </button>
          </div>
        </div>
      </aside>

      <!-- Main -->
      <div class="flex-1 flex flex-col">
        <!-- Topbar (mobile) -->
        <div class="md:hidden flex items-center justify-between px-4 h-14 border-b border-white/10 bg-gray-900/80 backdrop-blur">
          <button id="mobileMenuBtn" class="p-2 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-800/60">
            <i data-lucide="menu" class="w-5 h-5"></i>
          </button>
          <div class="text-sm font-semibold tracking-tight">Tablou de Bord</div>
          <div class="flex items-center gap-2">
            <button id="themeToggleMobile" class="p-2 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-800/60" title="Mod lumină/întuneric">
              <i data-lucide="moon" class="w-5 h-5"></i>
            </button>
          </div>
        </div>

        <!-- Header -->
        <header class="sticky top-0 z-30 bg-gray-900/75 backdrop-blur border-b border-white/10">
          <div class="flex items-center justify-between px-6 h-16">
            <div class="flex items-center gap-3">
              <button id="sidebarOpen" class="hidden md:hidden p-2 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-800/60">
                <i data-lucide="menu" class="w-5 h-5"></i>
              </button>
              <h1 class="text-lg md:text-xl font-semibold tracking-tight">Tablou de Bord</h1>
              <span class="hidden md:inline-flex items-center gap-2 text-xs text-gray-400 border border-white/10 rounded-md px-2 py-1">
                <i data-lucide="calendar" class="w-3.5 h-3.5"></i>
                Astăzi, 12 Oct 2025
              </span>
            </div>
            <div class="flex items-center gap-3">
              <button id="themeToggle" class="hidden md:inline-flex items-center gap-2 px-3 h-9 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-800/60 text-sm">
                <i data-lucide="moon" class="w-4.5 h-4.5"></i>
                <span class="hidden lg:inline">Mod</span>
              </button>
              <button class="relative p-2 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-800/60" title="Notificări">
                <i data-lucide="bell" class="w-5 h-5"></i>
                <span class="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-cyan-400 rounded-full ring-2 ring-gray-900"></span>
              </button>
              <button class="inline-flex items-center gap-2 bg-cyan-500 text-gray-900 font-medium text-sm h-10 px-4 rounded-md hover:bg-cyan-400 transition-colors border border-cyan-400/50" id="addAppointmentBtn">
                <i data-lucide="plus" class="w-4.5 h-4.5"></i>
                Adaugă Programare Manuală
              </button>
            </div>
          </div>
        </header>

        <!-- Content -->
        <main class="flex-1 px-4 md:px-6 py-6">
          <!-- KPI row -->
          <section class="flex md:grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3 md:gap-4 mb-6 overflow-x-auto md:overflow-visible -mx-4 px-4 snap-x snap-mandatory">
            <!-- KPI: Programări Azi -->
            <div data-surface="card" class="group relative overflow-hidden rounded-lg bg-gray-800/60 border border-white/10 p-4 hover:border-cyan-500/40 transition-colors min-w-[260px] md:min-w-0 snap-start">
              <div class="flex items-start justify-between">
                <div class="flex items-center gap-2">
                  <div class="p-2 rounded-md bg-cyan-500/10 border border-cyan-500/30">
                    <i data-lucide="calendar-check" class="w-4.5 h-4.5 text-cyan-400"></i>
                  </div>
                  <div class="text-sm text-gray-300">Programări Azi</div>
                </div>
                <span class="text-xs text-gray-400">08:00–18:00</span>
              </div>
              <div class="mt-3 flex items-end justify-between">
                <div>
                  <div class="text-2xl font-semibold tracking-tight">14</div>
                  <div class="text-xs text-emerald-400 mt-1 inline-flex items-center gap-1">
                    <i data-lucide="trending-up" class="w-3.5 h-3.5"></i>
                    +2 față de ieri
                  </div>
                </div>
                <div class="w-24">
                  <div class="h-12">
                    <div class="w-full h-full rounded-md bg-gray-900/40 border border-white/10 grid place-items-center text-[10px] text-gray-400">timeline</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- KPI: Venit Estimat -->
            <div data-surface="card" class="relative overflow-hidden rounded-lg bg-gray-800/60 border border-white/10 p-4 hover:border-cyan-500/40 transition-colors min-w-[260px] md:min-w-0 snap-start">
              <div class="flex items-start justify-between">
                <div class="flex items-center gap-2">
                  <div class="p-2 rounded-md bg-cyan-500/10 border border-cyan-500/30">
                    <i data-lucide="banknote" class="w-4.5 h-4.5 text-cyan-400"></i>
                  </div>
                  <div class="text-sm text-gray-300">Venit Estimat</div>
                </div>
                <span class="text-xs text-gray-400">azi</span>
              </div>
              <div class="mt-3 flex items-end justify-between">
                <div>
                  <div class="text-2xl font-semibold tracking-tight">1.250 RON</div>
                  <div class="text-xs text-gray-400 mt-1">Medie: 1.180 RON</div>
                </div>
                <div class="w-28">
                  <div class="relative h-14">
                    <div class="rounded-md bg-gray-900/40 border border-white/10 h-full px-1.5 py-1">
                      <div class="h-full">
                        <div>
                          <div class="relative h-full">
                            <div class="h-full">
                              <div class="h-full">
                                <div class="h-full">
                                  <!-- Chart container -->
                                  <div class="h-full">
                                    <div class="h-full">
                                      <div class="h-full">
                                        <div class="h-full">
                                          <div class="h-full">
                                            <div class="h-full">
                                              <div class="h-full">
                                                <div class="h-full">
                                                  <div class="h-full">
                                                    <div class="h-full">
                                                      <div class="h-full">
                                                        <div class="h-full">
                                                          <div class="h-full">
                                                            <div class="h-full">
                                                              <div class="h-full">
                                                                <div class="h-full">
                                                                  <div class="h-full">
                                                                    <div class="h-full">
                                                                      <div class="h-full">
                                                                        <div class="h-full">
                                                                          <div class="h-full">
                                                                            <div class="h-full">
                                                                              <div class="h-full">
                                                                                <div class="h-full">
                                                                                  <div class="h-full">
                                                                                    <div class="h-full">
                                                                                      <div class="h-full">
                                                                                        <div class="h-full">
                                                                                          <div class="h-full">
                                                                                            <div class="h-full">
                                                                                              <div class="h-full">
                                                                                                <div class="h-full">
                                                                                                  <div class="h-full">
                                                                                                    <div class="h-full">
                                                                                                      <div class="h-full">
                                                                                                        <div class="h-full">
                                                                                                          <div class="h-full">
                                                                                                            <div class="h-full">
                                                                                                              <div class="h-full">
                                                                                                                <div class="h-full">
                                                                                                                  <div class="h-full">
                                                                                                                    <div class="h-full">
                                                                                                                      <div class="h-full">
                                                                                                                        <div class="h-full">
                                                                                                                          <div class="h-full">
                                                                                                                            <div class="h-full">
                                                                                                                              <div class="h-full">
                                                                                                                                <div class="h-full">
                                                                                                                                  <div class="h-full">
                                                                                                                                    <div class="h-full">
                                                                                                                                      <div class="h-full">
                                                                                                                                        <div class="h-full">
                                                                                                                                          <div class="h-full">
                                                                                                                                            <div class="h-full">
                                                                                                                                              <div class="h-full">
                                                                                                                                                <div class="h-full">
                                                                                                                                                  <div class="h-full">
                                                                                                                                                    <div class="h-full">
                                                                                                                                                      <div class="h-full">
                                                                                                                                                        <div class="h-full">
                                                                                                                                                          <div class="h-full">
                                                                                                                                                            <div class="h-full">
                                                                                                                                                              <div class="h-full">
                                                                                                                                                                <div class="h-full">
                                                                                                                                                                  <div class="h-full">
                                                                                                                                                                    <div class="h-full">
                                                                                                                                                                      <div class="h-full">
                                                                                                                                                                        <div class="h-full">
                                                                                                                                                                          <div class="h-full">
                                                                                                                                                                            <div class="h-full">
                                                                                                                                                                              <div class="h-full">
                                                                                                                                                                                <div class="h-full">
                                                                                                                                                                                  <div class="h-full">
                                                                                                                                                                                    <div class="h-full">
                                                                                                                                                                                      <div class="h-full">
                                                                                                                                                                                        <div class="h-full">
                                                                                                                                                                                          <div class="h-full">
                                                                                                                                                                                            <div class="h-full">
                                                                                                                                                                                              <div class="h-full">
                                                                                                                                                                                                <div class="h-full">
                                                                                                                                                                                                  <div class="h-full">
                                                                                                                                                                                                    <div class="h-full">
                                                                                                                                                                                                      <div class="h-full">
                                                                                                                                                                                                        <div class="h-full">
                                                                                                                                                                                                          <div class="h-full">
                                                                                                                                                                                                            <div class="h-full">
                                                                                                                                                                                                              <div class="h-full">
                                                                                                                                                                                                                <div class="h-full">
                                                                                                                                                                                                                  <div class="h-full">
                                                                                                                                                                                                                    <div class="h-full">
                                                                                                                                                                                                                      <div class="h-full">
                                                                                                                                                                                                                        <div class="h-full">
                                                                                                                                                                                                                          <div class="h-full">
                                                                                                                                                                                                                            <div class="h-full">
                                                                                                                                                                                                                              <div class="h-full">
                                                                                                                                                                                                                                <div class="h-full">
                                                                                                                                                                                                                                  <div class="h-full">
                                                                                                                                                                                                                                    <div class="h-full">
                                                                                                                                                                                                                                      <div class="h-full">
                                                                                                                                                                                                                                        <div class="h-full">
                                                                                                                                                                                                                                          <div class="h-full">
                                                                                                                                                                                                                                            <div class="h-full">
                                                                                                                                                                                                                                              <div class="h-full">
                                                                                                                                                                                                                                                <div class="h-full">
                                                                                                                                                                                                                                                  <div class="h-full">
                                                                                                                                                                                                                                                    <div class="h-full">
                                                                                                                                                                                                                                                      <div class="h-full">
                                                                                                                                                                                                                                                        <div class="h-full">
                                                                                                                                                                                                                                                          <div class="h-full">
                                                                                                                                                                                                                                                            <div class="h-full">
                                                                                                                                                                                                                                                              <div class="h-full">
                                                                                                                                                                                                                                                                <div class="h-full">
                                                                                                                                                                                                                                                                  <!-- Important: canvas wrapped inside div to avoid growth bug -->
                                                                                                                                                                                                  <div class="h-full">
                                                                                                                                                                                                    <canvas id="revenueSparkline"></canvas>
                                                                                                                                                                                                  </div>
                                                                                                                                                                                                                                                                </div>
                                                                                                                                                                                                                                                              </div>
                                                                                                                                                                                                                                                            </div>
                                                                                                                                                                                                                                                          </div>
                                                                                                                                                                                                                                                        </div>
                                                                                                                                                                                                                                                      </div>
                                                                                                                                                                                                                                                    </div>
                                                                                                                                                                                                                                                  </div>
                                                                                                                                                                                                                                                </div>
                                                                                                                                                                                                                                              </div>
                                                                                                                                                                                                                                            </div>
                                                                                                                                                                                                                                          </div>
                                                                                                                                                                                                                                        </div>
                                                                                                                                                                                                                                      </div>
                                                                                                                                                                                                                                    </div>
                                                                                                                                                                                                                                  </div>
                                                                                                                                                                                                                                </div>
                                                                                                                                                                                                                              </div>
                                                                                                                                                                                                                            </div>
                                                                                                                                                                                                                          </div>
                                                                                                                                                                                                                        </div>
                                                                                                                                                                                                                      </div>
                                                                                                                                                                                                                    </div>
                                                                                                                                                                                                                  </div>
                                                                                                                                                                                                                </div>
                                                                                                                                                                                                              </div>
                                                                                                                                                                                                            </div>
                                                                                                                                                                                                          </div>
                                                                                                                                                                                                        </div>
                                                                                                                                                                                                      </div>
                                                                                                                                                                                                    </div>
                                                                                                                                                                                                  </div>
                                                                                                                                                                                                </div>
                                                                                                                                                                                              </div>
                                                                                                                                                                                            </div>
                                                                                                                                                                                          </div>
                                                                                                                                                                                        </div>
                                                                                                                                                                                      </div>
                                                                                                                                                                                    </div>
                                                                                                                                                                                  </div>
                                                                                                                                                                                </div>
                                                                                                                                                                              </div>
                                                                                                                                                                            </div>
                                                                                                                                                                          </div>
                                                                                                                                                                        </div>
                                                                                                                                                                      </div>
                                                                                                                                                                    </div>
                                                                                                                                  <!-- end nested -->
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- KPI: Grad de Ocupare -->
            <div data-surface="card" class="relative overflow-hidden rounded-lg bg-gray-800/60 border border-white/10 p-4 hover:border-cyan-500/40 transition-colors min-w-[260px] md:min-w-0 snap-start">
              <div class="flex items-start justify-between">
                <div class="flex items-center gap-2">
                  <div class="p-2 rounded-md bg-cyan-500/10 border border-cyan-500/30">
                    <i data-lucide="clock-9" class="w-4.5 h-4.5 text-cyan-400"></i>
                  </div>
                  <div class="text-sm text-gray-300">Grad de Ocupare</div>
                </div>
                <span class="text-xs text-gray-400">azi</span>
              </div>
              <div class="mt-3 flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class="w-16 h-16 rounded-full bg-gray-900/40 border border-white/10 grid place-items-center">
                    <div class="w-14 h-14">
                      <div class="h-full">
                        <div class="h-full">
                          <div class="h-full">
                            <div class="h-full">
                              <div class="h-full">
                                <div class="h-full">
                                  <div class="h-full">
                                    <div class="h-full">
                                      <div class="h-full">
                                        <div class="h-full">
                                          <div class="h-full">
                                            <div class="h-full">
                                              <div class="h-full">
                                                <div class="h-full">
                                                  <div class="h-full">
                                                    <div class="h-full">
                                                      <!-- wrapped canvas -->
                                                      <div class="h-full">
                                                        <canvas id="occupancyDonut"></canvas>
                                                      </div>
                                                    </div>
                                                  </div>
                                                </div>
                                              </div>
                                            </div>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div>
                    <div class="text-2xl font-semibold tracking-tight">85%</div>
                    <div class="text-xs text-gray-400">Sloturi ocupate</div>
                  </div>
                </div>
                <div class="text-xs text-emerald-400 inline-flex items-center gap-1">
                  <i data-lucide="arrow-up-right" class="w-3.5 h-3.5"></i>
                  +3% vs. săptămâna trecută
                </div>
              </div>
            </div>

            <!-- KPI: Rata de Succes AI -->
            <div data-surface="card" class="relative overflow-hidden rounded-lg bg-gray-800/60 border border-white/10 p-4 hover:border-cyan-500/40 transition-colors min-w-[260px] md:min-w-0 snap-start">
              <div class="flex items-start justify-between">
                <div class="flex items-center gap-2">
                  <div class="p-2 rounded-md bg-cyan-500/10 border border-cyan-500/30">
                    <i data-lucide="bot" class="w-4.5 h-4.5 text-cyan-400"></i>
                  </div>
                  <div class="text-sm text-gray-300">Rata de Succes AI</div>
                </div>
                <span class="text-xs text-gray-400">ultimele 24h</span>
              </div>
              <div class="mt-3 flex items-end justify-between">
                <div>
                  <div class="text-2xl font-semibold tracking-tight">92%</div>
                  <div class="text-xs text-gray-400 mt-1">Programări finalizate automat</div>
                </div>
                <div class="inline-flex items-center gap-2 text-xs">
                  <span class="text-emerald-400 inline-flex items-center gap-1">
                    <i data-lucide="check-circle" class="w-3.5 h-3.5"></i> 46
                  </span>
                  <span class="text-amber-300 inline-flex items-center gap-1">
                    <i data-lucide="clock" class="w-3.5 h-3.5"></i> 3
                  </span>
                  <span class="text-red-400 inline-flex items-center gap-1">
                    <i data-lucide="x-circle" class="w-3.5 h-3.5"></i> 1
                  </span>
                </div>
              </div>
            </div>
          </div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></div></section>

          <!-- Main grid -->
          <section class="grid grid-cols-1 xl:grid-cols-12 gap-6">
            <!-- Agenda Zilei -->
            <div class="xl:col-span-8">
              <div data-surface="card" class="rounded-lg bg-gray-800/60 border border-white/10 overflow-hidden">
                <div class="flex items-center justify-between p-4 border-b border-white/10">
                  <div class="flex items-center gap-2">
                    <i data-lucide="timeline" class="w-4.5 h-4.5 text-cyan-400"></i>
                    <h2 class="text-base md:text-lg font-semibold tracking-tight">Agenda Zilei</h2>
                  </div>
                  <div class="flex items-center gap-2 text-xs">
                    <button class="px-2.5 h-8 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-700/40 transition">Astăzi</button>
                    <button class="px-2.5 h-8 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-700/40 transition">
                      <i data-lucide="chevron-left" class="w-4 h-4"></i>
                    </button>
                    <button class="px-2.5 h-8 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-700/40 transition">
                      <i data-lucide="chevron-right" class="w-4 h-4"></i>
                    </button>
                  </div>
                </div>

                <div class="p-4">
                  <!-- Timeline grid -->
                  <div class="grid grid-cols-12 gap-3 md:gap-4">
                    <!-- Hours rail -->
                    <div class="hidden md:block md:col-span-2">
                      <div class="space-y-6 text-xs text-gray-400">
                        <div>08:00</div>
                        <div>09:00</div>
                        <div>10:00</div>
                        <div>11:00</div>
                        <div>12:00</div>
                        <div>13:00</div>
                        <div>14:00</div>
                        <div>15:00</div>
                        <div>16:00</div>
                        <div>17:00</div>
                        <div>18:00</div>
                      </div>
                    </div>
                    <!-- Appointments -->
                    <div class="col-span-12 md:col-span-10">
                      <div class="relative">
                        <!-- vertical guide -->
                        <div class="absolute left-0 top-0 bottom-0 w-px bg-white/10"></div>
                        <div class="space-y-3 pl-0 md:pl-4">
                          <!-- 08:30 Appointment -->
                          <div class="relative">
                            <div class="absolute -left-[18px] top-3 w-2 h-2 bg-emerald-400 rounded-full ring-2 ring-gray-900"></div>
                            <div class="flex items-center justify-between rounded-md border border-white/10 bg-gray-900/40 hover:border-cyan-500/40 transition p-3">
                              <div class="flex items-center gap-3">
                                <span class="text-xs text-gray-400 w-14 md:w-16">08:30</span>
                                <div class="flex flex-col">
                                  <div class="text-sm font-medium">Ion P.</div>
                                  <div class="text-xs text-gray-400">Tuns simplu</div>
                                  <div class="mt-1 flex items-center gap-2">
                                    <span class="inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded border border-emerald-500/30 text-emerald-400 bg-emerald-500/10">Confirmat</span>
                                    <span class="inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded border border-cyan-500/30 text-cyan-300 bg-cyan-500/10">
                                      <i data-lucide="mic" class="w-3.5 h-3.5"></i> Voce
                                    </span>
                                  </div>
                                </div>
                              </div>
                              <button class="p-2 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-800/60">
                                <i data-lucide="ellipsis" class="w-4.5 h-4.5"></i>
                              </button>
                            </div>
                          </div>

                          <!-- 10:00 Pending -->
                          <div class="relative">
                            <div class="absolute -left-[18px] top-3 w-2 h-2 bg-amber-300 rounded-full ring-2 ring-gray-900"></div>
                            <div class="flex items-center justify-between rounded-md border border-white/10 bg-gray-900/40 hover:border-cyan-500/40 transition p-3">
                              <div class="flex items-center gap-3">
                                <span class="text-xs text-gray-400 w-14 md:w-16">10:00</span>
                                <div class="flex flex-col">
                                  <div class="text-sm font-medium">Maria L.</div>
                                  <div class="text-xs text-gray-400">Tuns + Vopsit</div>
                                  <div class="mt-1 flex items-center gap-2">
                                    <span class="inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded border border-amber-300/40 text-amber-200 bg-amber-300/10">În așteptare</span>
                                    <span class="inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded border border-white/15 text-gray-300 bg-white/5">
                                      <i data-lucide="keyboard" class="w-3.5 h-3.5"></i> Manual
                                    </span>
                                  </div>
                                </div>
                              </div>
                              <button class="p-2 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-800/60">
                                <i data-lucide="ellipsis" class="w-4.5 h-4.5"></i>
                              </button>
                            </div>
                          </div>

                          <!-- 11:00 Break -->
                          <div class="relative">
                            <div class="absolute -left-[18px] top-3 w-2 h-2 bg-sky-400 rounded-full ring-2 ring-gray-900"></div>
                            <div class="flex items-center justify-between rounded-md border border-dashed border-white/15 bg-gray-900/20 p-3">
                              <div class="flex items-center gap-3">
                                <span class="text-xs text-gray-400 w-14 md:w-16">11:00</span>
                                <div class="text-xs text-gray-400">Pauză scurtă (15 min)</div>
                              </div>
                            </div>
                          </div>

                          <!-- 11:30 Next highlighted -->
                          <div class="relative">
                            <div class="absolute -left-[18px] top-3 w-2 h-2 bg-emerald-400 rounded-full ring-2 ring-gray-900"></div>
                            <div class="flex items-center justify-between rounded-md border border-cyan-400/40 bg-cyan-500/5 ring-2 ring-cyan-400/20 p-3">
                              <div class="flex items-center gap-3">
                                <span class="text-xs text-cyan-300 w-14 md:w-16">11:30</span>
                                <div class="flex flex-col">
                                  <div class="text-sm font-medium text-white">Mihai V.</div>
                                  <div class="text-xs text-gray-300">Tuns + Barbă</div>
                                  <div class="mt-1 flex items-center gap-2">
                                    <span class="inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded border border-emerald-500/30 text-emerald-400 bg-emerald-500/10">Confirmat</span>
                                    <span class="inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded border border-cyan-500/30 text-cyan-300 bg-cyan-500/10">
                                      <i data-lucide="mic" class="w-3.5 h-3.5"></i> Voce
                                    </span>
                                    <span class="inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded border border-cyan-500/30 text-cyan-300 bg-cyan-500/10">
                                      Următorul
                                    </span>
                                  </div>
                                </div>
                              </div>
                              <button class="p-2 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-800/60">
                                <i data-lucide="ellipsis" class="w-4.5 h-4.5"></i>
                              </button>
                            </div>
                          </div>

                          <!-- 12:30 Lunch Break -->
                          <div class="relative">
                            <div class="absolute -left-[18px] top-3 w-2 h-2 bg-sky-400 rounded-full ring-2 ring-gray-900"></div>
                            <div class="flex items-center justify-between rounded-md border border-dashed border-white/15 bg-gray-900/20 p-3">
                              <div class="flex items-center gap-3">
                                <span class="text-xs text-gray-400 w-14 md:w-16">12:30</span>
                                <div class="text-xs text-gray-400">Pauză prânz (30 min)</div>
                              </div>
                            </div>
                          </div>

                          <!-- 13:30 Confirmed -->
                          <div class="relative">
                            <div class="absolute -left-[18px] top-3 w-2 h-2 bg-emerald-400 rounded-full ring-2 ring-gray-900"></div>
                            <div class="flex items-center justify-between rounded-md border border-white/10 bg-gray-900/40 hover:border-cyan-500/40 transition p-3">
                              <div class="flex items-center gap-3">
                                <span class="text-xs text-gray-400 w-14 md:w-16">13:30</span>
                                <div class="flex flex-col">
                                  <div class="text-sm font-medium">Andrei C.</div>
                                  <div class="text-xs text-gray-400">Tuns</div>
                                  <div class="mt-1 flex items-center gap-2">
                                    <span class="inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded border border-emerald-500/30 text-emerald-400 bg-emerald-500/10">Confirmat</span>
                                    <span class="inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded border border-white/15 text-gray-300 bg-white/5">
                                      <i data-lucide="keyboard" class="w-3.5 h-3.5"></i> Manual
                                    </span>
                                  </div>
                                </div>
                              </div>
                              <button class="p-2 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-800/60">
                                <i data-lucide="ellipsis" class="w-4.5 h-4.5"></i>
                              </button>
                            </div>
                          </div>

                          <!-- 14:30 Current -->
                          <div class="relative">
                            <div class="absolute -left-[18px] top-3 w-2 h-2 bg-cyan-400 rounded-full ring-2 ring-gray-900"></div>
                            <div class="flex items-center justify-between rounded-md border border-cyan-400/40 bg-cyan-500/5 backdrop-blur-sm p-3">
                              <div class="flex items-center gap-3">
                                <span class="text-xs text-cyan-300 w-14 md:w-16">14:30</span>
                                <div class="flex flex-col">
                                  <div class="text-sm font-medium">Clientul Actual</div>
                                  <div class="text-xs text-gray-300">Tuns + Spălat</div>
                                  <div class="mt-1 flex items-center gap-2">
                                    <span class="inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded border border-emerald-500/30 text-emerald-400 bg-emerald-500/10">În desfășurare</span>
                                    <span class="inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded border border-cyan-500/30 text-cyan-300 bg-cyan-500/10">
                                      <i data-lucide="mic" class="w-3.5 h-3.5"></i> Voce
                                    </span>
                                  </div>
                                </div>
                              </div>
                              <button class="p-2 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-800/60">
                                <i data-lucide="ellipsis" class="w-4.5 h-4.5"></i>
                              </button>
                            </div>
                          </div>

                          <!-- 15:30 Canceled -->
                          <div class="relative">
                            <div class="absolute -left-[18px] top-3 w-2 h-2 bg-red-400 rounded-full ring-2 ring-gray-900"></div>
                            <div class="flex items-center justify-between rounded-md border border-white/10 bg-gray-900/40 hover:border-cyan-500/40 transition p-3">
                              <div class="flex items-center gap-3">
                                <span class="text-xs text-gray-400 w-14 md:w-16">15:30</span>
                                <div class="flex flex-col">
                                  <div class="text-sm font-medium">Anulat</div>
                                  <div class="text-xs text-gray-400">Tuns + Barbă</div>
                                  <div class="mt-1 flex items-center gap-2">
                                    <span class="inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded border border-red-400/40 text-red-300 bg-red-400/10">Anulat</span>
                                    <span class="inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded border border-white/15 text-gray-300 bg-white/5">
                                      <i data-lucide="keyboard" class="w-3.5 h-3.5"></i> Manual
                                    </span>
                                  </div>
                                </div>
                              </div>
                              <button class="p-2 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-800/60">
                                <i data-lucide="ellipsis" class="w-4.5 h-4.5"></i>
                              </button>
                            </div>
                          </div>

                          <!-- 16:30 Free slot example -->
                          <div class="relative">
                            <div class="absolute -left-[18px] top-3 w-2 h-2 bg-gray-500 rounded-full ring-2 ring-gray-900"></div>
                            <div class="flex items-center justify-between rounded-md border border-dashed border-white/15 bg-gray-900/20 p-3">
                              <div class="flex items-center gap-3">
                                <span class="text-xs text-gray-400 w-14 md:w-16">16:30</span>
                                <div class="text-xs text-gray-400">Slot liber</div>
                              </div>
                              <button class="inline-flex items-center gap-1.5 px-2.5 h-8 rounded-md border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/10">
                                <i data-lucide="plus" class="w-4 h-4"></i>
                                Adaugă
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div> <!-- end appointments -->
                  </div>
                </div>
              </div>
            </div>

            <!-- Voice Agent Monitor + Alerts -->
            <div class="xl:col-span-4 space-y-6">
              <!-- Monitorizare Agent Vocal -->
              <div data-surface="card" class="rounded-lg bg-gray-800/60 border border-white/10 overflow-hidden">
                <div class="flex items-center justify-between p-4 border-b border-white/10">
                  <div class="flex items-center gap-2">
                    <i data-lucide="waveform" class="w-4.5 h-4.5 text-cyan-400"></i>
                    <h3 class="text-base font-semibold tracking-tight">Agent Vocal — Activitate</h3>
                  </div>
                  <button class="px-2.5 h-8 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-700/40 text-xs transition">Live</button>
                </div>
                <div class="divide-y divide-white/10">
                  <!-- Entry success -->
                  <div class="p-4 flex items-start gap-3">
                    <span class="mt-1.5 w-2 h-2 rounded-full bg-emerald-400"></span>
                    <div class="flex-1">
                      <div class="flex items-center justify-between">
                        <div class="text-sm">
                          <span class="text-gray-300">[14:30]</span>
                          <span class="ml-2 text-gray-100">Intenție:</span>
                          <span class="text-gray-300">"Tuns simplu"</span>
                        </div>
                        <span class="text-xs inline-flex items-center gap-1 text-emerald-400">
                          <i data-lucide="check-circle" class="w-3.5 h-3.5"></i>
                          Programare reușită (Mihai V.)
                        </span>
                      </div>
                      <div class="mt-2">
                        <button class="inline-flex items-center gap-1.5 text-xs text-cyan-300 hover:text-cyan-200">
                          <i data-lucide="file-text" class="w-3.5 h-3.5"></i>
                          Vezi transcrierea
                        </button>
                      </div>
                    </div>
                  </div>
                  <!-- Entry warning -->
                  <div class="p-4 flex items-start gap-3">
                    <span class="mt-1.5 w-2 h-2 rounded-full bg-amber-300"></span>
                    <div class="flex-1">
                      <div class="flex items-center justify-between">
                        <div class="text-sm">
                          <span class="text-gray-300">[14:25]</span>
                          <span class="ml-2 text-gray-100">Intenție:</span>
                          <span class="text-gray-300">"Vopsit"</span>
                        </div>
                        <span class="text-xs inline-flex items-center gap-1 text-amber-200">
                          <i data-lucide="alert-circle" class="w-3.5 h-3.5"></i>
                          Serviciu neconfigurat
                        </span>
                      </div>
                      <div class="text-xs text-gray-400 mt-1">Rezultat: Conversație abandonată</div>
                      <div class="mt-2">
                        <button class="inline-flex items-center gap-1.5 text-xs text-cyan-300 hover:text-cyan-200">
                          <i data-lucide="file-text" class="w-3.5 h-3.5"></i>
                          Vezi transcrierea
                        </button>
                      </div>
                    </div>
                  </div>
                  <!-- Entry error -->
                  <div class="p-4 flex items-start gap-3">
                    <span class="mt-1.5 w-2 h-2 rounded-full bg-red-400"></span>
                    <div class="flex-1">
                      <div class="flex items-center justify-between">
                        <div class="text-sm">
                          <span class="text-gray-300">[14:20]</span>
                          <span class="ml-2 text-gray-100">Eroare Sistem:</span>
                          <span class="text-gray-300">Sincronizare Google Calendar eșuată</span>
                        </div>
                        <span class="text-xs inline-flex items-center gap-1 text-red-300">
                          <i data-lucide="x-octagon" class="w-3.5 h-3.5"></i>
                          Intervenție necesară
                        </span>
                      </div>
                      <div class="mt-2">
                        <button class="inline-flex items-center gap-1.5 text-xs text-cyan-300 hover:text-cyan-200">
                          <i data-lucide="file-text" class="w-3.5 h-3.5"></i>
                          Vezi log-ul
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Alerte & Sincronizare -->
              <div data-surface="card" class="rounded-lg bg-gray-800/60 border border-white/10 overflow-hidden">
                <div class="flex items-center justify-between p-4 border-b border-white/10">
                  <div class="flex items-center gap-2">
                    <i data-lucide="shield-alert" class="w-4.5 h-4.5 text-cyan-400"></i>
                    <h3 class="text-base font-semibold tracking-tight">Alerte &amp; Sincronizare</h3>
                  </div>
                </div>
                <div class="p-4 space-y-3">
                  <div class="flex items-center justify-between rounded-md border border-white/10 bg-gray-900/40 p-3">
                    <div class="flex items-center gap-2">
                      <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                      <div class="text-sm">OpenAI API</div>
                    </div>
                    <div class="text-xs text-emerald-300 inline-flex items-center gap-1">
                      <i data-lucide="check" class="w-3.5 h-3.5"></i>
                      Online
                    </div>
                  </div>
                  <div class="flex items-center justify-between rounded-md border border-white/10 bg-gray-900/40 p-3">
                    <div class="flex items-center gap-2">
                      <span class="w-2.5 h-2.5 rounded-full bg-red-400"></span>
                      <div class="text-sm">Google Calendar</div>
                    </div>
                    <div class="text-xs text-red-300 inline-flex items-center gap-1">
                      <i data-lucide="x" class="w-3.5 h-3.5"></i>
                      Offline
                    </div>
                  </div>
                  <div class="flex items-center justify-between rounded-md border border-white/10 bg-gray-900/40 p-3">
                    <div class="flex items-center gap-2">
                      <span class="w-2.5 h-2.5 rounded-full bg-amber-300"></span>
                      <div class="text-sm">Ultima anulare</div>
                    </div>
                    <div class="text-xs text-amber-200">acum 12 min</div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>

    <!-- Mobile sidebar drawer -->
    <div id="mobileDrawer" class="fixed inset-0 z-40 hidden">
      <div id="drawerBackdrop" class="absolute inset-0 bg-black/50"></div>
      <div class="absolute left-0 top-0 bottom-0 w-72 bg-gray-800 border-r border-white/10 p-4">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <div class="grid place-items-center w-8 h-8 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 tracking-tight text-sm font-semibold">VB</div>
            <div class="text-sm font-semibold tracking-tight">Voice Booking</div>
          </div>
          <button id="drawerClose" class="p-2 rounded-md border border-white/10 hover:border-white/20 hover:bg-gray-700/40">
            <i data-lucide="x" class="w-5 h-5"></i>
          </button>
        </div>
        <nav class="space-y-1">
          <a href="#" class="flex items-center gap-3 px-3 py-2 rounded-md text-sm bg-gray-700/50 border border-white/10">
            <i data-lucide="layout-dashboard" class="w-4.5 h-4.5 text-cyan-400"></i>
            Dashboard
          </a>
          <a href="#" class="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-300 hover:text-white hover:bg-gray-700/40 border border-transparent hover:border-white/10">
            <i data-lucide="calendar" class="w-4.5 h-4.5"></i>
            Calendar
          </a>
          <a href="#" class="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-300 hover:text-white hover:bg-gray-700/40 border border-transparent hover:border-white/10">
            <i data-lucide="users" class="w-4.5 h-4.5"></i>
            Clienți
          </a>
          <a href="#" class="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-300 hover:text-white hover:bg-gray-700/40 border border-transparent hover:border-white/10">
            <i data-lucide="scissors" class="w-4.5 h-4.5"></i>
            Servicii &amp; Prețuri
          </a>
          <a href="#" class="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-300 hover:text-white hover:bg-gray-700/40 border border-transparent hover:border-white/10">
            <i data-lucide="chart-line" class="w-4.5 h-4.5"></i>
            Statistici
          </a>
          <a href="#" class="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-gray-300 hover:text-white hover:bg-gray-700/40 border border-transparent hover:border-white/10">
            <i data-lucide="mic" class="w-4.5 h-4.5"></i>
            Setări Agent Vocal
          </a>
        </nav>
      </div>
    </div>

    <script>
      // Init icons with 1.5 stroke width
      document.addEventListener('DOMContentLoaded', () => {
        if (window.lucide) {
          lucide.createIcons({ attrs: { 'stroke-width': 1.5 } });
        }
        // Charts
        const revenueCtx = document.getElementById('revenueSparkline');
        if (revenueCtx) {
          new Chart(revenueCtx, {
            type: 'line',
            data: {
              labels: ['L', 'Ma', 'Mi', 'J', 'V', 'S', 'D'],
              datasets: [{
                data: [920, 1080, 980, 1180, 1250, 1020, 0],
                borderColor: '#06B6D4',
                backgroundColor: 'rgba(6,182,212,0.15)',
                tension: 0.4,
                fill: true,
                pointRadius: 0
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: { legend: { display: false }, tooltip: { enabled: false } },
              scales: {
                x: { display: false, grid: { display: false } },
                y: { display: false, grid: { display: false } }
              },
              elements: { line: { borderWidth: 2 } }
            }
          });
        }

        const occupancyCtx = document.getElementById('occupancyDonut');
        if (occupancyCtx) {
          new Chart(occupancyCtx, {
            type: 'doughnut',
            data: {
              labels: ['Ocupat', 'Liber'],
              datasets: [{
                data: [85, 15],
                backgroundColor: ['#06B6D4', 'rgba(255,255,255,0.08)'],
                borderWidth: 0
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              cutout: '70%',
              plugins: { legend: { display: false }, tooltip: { enabled: false } }
            }
          });
        }

        // Mobile drawer
        const mobileBtn = document.getElementById('mobileMenuBtn');
        const drawer = document.getElementById('mobileDrawer');
        const drawerClose = document.getElementById('drawerClose');
        const drawerBackdrop = document.getElementById('drawerBackdrop');
        const toggleDrawer = (open) => {
          drawer.classList.toggle('hidden', !open);
        };
        if (mobileBtn) mobileBtn.addEventListener('click', () => toggleDrawer(true));
        if (drawerClose) drawerClose.addEventListener('click', () => toggleDrawer(false));
        if (drawerBackdrop) drawerBackdrop.addEventListener('click', () => toggleDrawer(false));

        // Theme toggle: default dark, allow light mode
        const applyTheme = (mode) => {
          const isLight = mode === 'light';
          const body = document.body;
          body.classList.toggle('bg-gray-900', !isLight);
          body.classList.toggle('text-gray-100', !isLight);
          body.classList.toggle('bg-gray-50', isLight);
          body.classList.toggle('text-gray-900', isLight);

          // Swap surfaces
          document.querySelectorAll('[data-surface="card"]').forEach(el => {
            el.classList.toggle('bg-gray-800/60', !isLight);
            el.classList.toggle('border-white/10', !isLight);
            el.classList.toggle('bg-white', isLight);
            el.classList.toggle('border-gray-200', isLight);
          });

          // Swap header/sidebar borders and backgrounds
          document.querySelectorAll('header, aside, #mobileDrawer .w-72').forEach(el => {
            el.classList.toggle('bg-gray-900/75', !isLight);
            el.classList.toggle('bg-white/80', isLight);
            el.classList.toggle('backdrop-blur', true);
            el.classList.toggle('border-white/10', !isLight);
            el.classList.toggle('border-gray-200', isLight);
          });

          // Save preference
          try { localStorage.setItem('theme', mode); } catch {}
        };

        const themeToggle = document.getElementById('themeToggle');
        const themeToggleMobile = document.getElementById('themeToggleMobile');
        const setTheme = () => {
          let saved = null;
          try { saved = localStorage.getItem('theme'); } catch {}
          const prefer = saved || 'dark';
          applyTheme(prefer);
        };
        if (themeToggle) themeToggle.addEventListener('click', () => {
          const current = (localStorage.getItem('theme') || 'dark');
          applyTheme(current === 'dark' ? 'light' : 'dark');
        });
        if (themeToggleMobile) themeToggleMobile.addEventListener('click', () => {
          const current = (localStorage.getItem('theme') || 'dark');
          applyTheme(current === 'dark' ? 'light' : 'dark');
        });
        setTheme();

        // CTA demo
        const addBtn = document.getElementById('addAppointmentBtn');
        if (addBtn) addBtn.addEventListener('click', () => {
          alert('Deschide formularul de adăugare programare (mock).');
        });
      });
    </script>
  
</body></html>