import React from 'react';
import { 
  LayoutDashboard, UploadCloud, ReceiptText, PieChart, 
  FileDown, History, Settings, ChevronLeft, ChevronRight, Zap,
  Moon, Sun, HelpCircle
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  collapsed: boolean;
  setCollapsed: (val: boolean) => void;
  darkMode: boolean;
  setDarkMode: (val: boolean) => void;
  onReturnHome: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  collapsed,
  setCollapsed,
  darkMode,
  setDarkMode,
  onReturnHome,
}) => {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload Statement', icon: UploadCloud },
    { id: 'transactions', label: 'Transactions', icon: ReceiptText },
    { id: 'analytics', label: 'Analytics', icon: PieChart },
    { id: 'export', label: 'Export Center', icon: FileDown },
    { id: 'history', label: 'History', icon: History },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside
      className={`relative flex flex-col justify-between border-r border-[#E9EAF2] dark:border-gray-800 bg-white dark:bg-[#121221] transition-all duration-300 z-20 ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand & Collapse */}
      <div>
        <div className="h-18 flex items-center justify-between px-5 border-b border-[#E9EAF2] dark:border-gray-800">
          <div 
            onClick={onReturnHome}
            className="flex items-center gap-3 cursor-pointer overflow-hidden"
          >
            <div className="w-10 h-10 rounded-xl bg-[#6C5CE7] flex items-center justify-center text-white shrink-0 shadow-md shadow-[#6C5CE7]/30">
              <Zap className="w-5 h-5 text-white" />
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="font-extrabold text-base tracking-tight text-[#17172B] dark:text-white">
                  Befree <span className="text-[#6C5CE7]">Intel</span>
                </span>
                <span className="text-[10px] text-[#73758A] dark:text-gray-400 font-semibold uppercase tracking-wider">
                  Fintech Suite
                </span>
              </div>
            )}
          </div>

          <button
            onClick={() => setCollapsed(!collapsed)}
            className="w-7 h-7 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center justify-center text-[#73758A] transition-colors"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1.5 mt-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                title={collapsed ? item.label : undefined}
                className={`w-full flex items-center gap-3.5 px-3.5 py-3 rounded-xl text-sm font-semibold transition-all group ${
                  isActive
                    ? 'bg-[#6C5CE7] text-white shadow-md shadow-[#6C5CE7]/25'
                    : 'text-[#73758A] dark:text-gray-400 hover:text-[#17172B] dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-800/60'
                }`}
              >
                <Icon
                  className={`w-5 h-5 shrink-0 transition-transform group-hover:scale-110 ${
                    isActive ? 'text-white' : 'text-[#73758A] dark:text-gray-400'
                  }`}
                />
                {!collapsed && <span className="truncate">{item.label}</span>}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer controls */}
      <div className="p-3 border-t border-[#E9EAF2] dark:border-gray-800 space-y-2">
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="w-full flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-sm font-medium text-[#73758A] dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          {darkMode ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5" />}
          {!collapsed && <span>{darkMode ? 'Light Theme' : 'Dark Theme'}</span>}
        </button>

        <div className={`flex items-center gap-3 px-3 py-2 text-xs text-[#73758A] ${collapsed ? 'justify-center' : ''}`}>
          <HelpCircle className="w-4 h-4 text-gray-400 shrink-0" />
          {!collapsed && <span className="text-[11px]">Befree v2.0 • Round 2</span>}
        </div>
      </div>
    </aside>
  );
};
