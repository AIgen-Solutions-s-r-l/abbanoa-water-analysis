# Forecast Dashboard Visual Design Mockup

## For Product Owner Review

### Overall Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    💧 Water Network Forecasting Dashboard                │
│                     Abbanoa Infrastructure Monitoring System             │
│                                                                         │
│  ┌─────────────────┐  ┌───────────────────────────────────────────────┐│
│  │                 │  │                                               ││
│  │ 🎛️ Forecast     │  │  📈 Forecast    Analytics    Anomaly   System ││
│  │ Parameters      │  │                                               ││
│  │                 │  │ ┌─────────────────────────────────────────┐ ││
│  │ District:       │  │ │  7-Day Forecast: DIST_001 - Flow Rate   │ ││
│  │ [DIST_001  ▼]  │  │ │                                           │ ││
│  │                 │  │ │     120 ┤                      ╱─────    │ ││
│  │ Metric:         │  │ │     110 ┤         ╱───────────╱      ╲   │ ││
│  │ [Flow Rate ▼]  │  │ │     100 ┤────────╱            ╱        ╲  │ ││
│  │                 │  │ │      90 ┤                    ╱          ╲ │ ││
│  │ Horizon:        │  │ │         └────────────────────┴───────────┘ │ ││
│  │ [====7====]     │  │ │         Historical ——— Forecast - - -      │ ││
│  │                 │  │ └─────────────────────────────────────────┘ ││
│  │ ───────────     │  │                                               ││
│  │                 │  │  ┌──────────────┐  ┌──────────────┐         ││
│  │ ⚙️ Display      │  │  │ Next Day     │  │ Confidence   │         ││
│  │ Options         │  │  │ 108.5 L/s    │  │ Score: 92%   │         ││
│  │                 │  │  │ ↑ +3.2%      │  │ High         │         ││
│  │ ☑ Confidence    │  │  └──────────────┘  └──────────────┘         ││
│  │ ☑ Historical    │  │                                               ││
│  │ ☐ Auto-refresh  │  │  Model: ARIMA_PLUS | Updated: 14:30:45      ││
│  │                 │  │                                               ││
│  │ ───────────     │  │  💾 Export Options                           ││
│  │                 │  │  [📥 Download CSV] [📥 Download JSON]        ││
│  └─────────────────┘  └───────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

### Color Scheme

#### Primary Colors
- **Primary Blue**: #1f77b4 (Headers, historical data, primary buttons)
- **Secondary Orange**: #ff7f0e (Forecast data, accents)
- **Success Green**: #2ca02c (Positive changes, download buttons)
- **Background White**: #ffffff (Main content area)
- **Surface Gray**: #f0f2f6 (Cards, sidebar background)

#### Data Visualization Colors
- **Historical Line**: Solid blue (#1f77b4)
- **Forecast Line**: Dashed orange (#ff7f0e)
- **Confidence Interval**: Semi-transparent orange (rgba(255, 127, 14, 0.2))
- **Grid Lines**: Light gray (#e0e0e0)
- **Now Marker**: Medium gray (#666666)

### Typography

- **Headers**: Inter 600 (Semi-bold)
- **Body Text**: Inter 400 (Regular)
- **Metrics**: Inter 700 (Bold)
- **Captions**: Inter 400 (Regular, smaller size)

### Component Details

#### 1. Header Section
- Centered title with water drop emoji
- Subtitle in smaller, muted text
- Clean, professional appearance
- Refresh button in top-right with timestamp

#### 2. Sidebar (Left Panel)
- Light gray background (#f0f2f6)
- Rounded corners on all inputs
- Clear section separators
- Expandable help sections at bottom
- Consistent 1rem padding

#### 3. Main Chart Area
- White background with subtle shadow
- Large, clear title
- Interactive Plotly chart with hover tooltips
- Smooth zoom and pan capabilities
- Download button in chart toolbar

#### 4. Metric Cards
- Elevated appearance with shadow
- Large, bold numbers
- Color-coded change indicators (green up, red down)
- Subtle hover effect (slight elevation)

#### 5. Interactive Elements

##### Dropdowns
```
┌─────────────────────┐
│ DIST_001         ▼ │  Clean white background
└─────────────────────┘  1px border (#e0e0e0)
                        Rounded corners (4px)
```

##### Slider
```
Min ○━━━━━━━━━━━━━● Max  Primary blue track
    1             7      Gray handle with shadow
```

##### Buttons
```
┌─────────────────────┐
│  📥 Download CSV    │  Green background
└─────────────────────┘  White text, no border
                        Slight shadow on hover
```

### Responsive Behavior

#### Desktop (>1024px)
- Full layout as shown above
- Sidebar fixed at 300px width
- Main content flexible width

#### Tablet (768-1024px)
- Sidebar reduces to 250px
- Metric cards stack vertically
- Chart maintains aspect ratio

#### Mobile (<768px)
- Sidebar moves to top (collapsible)
- Single column layout
- Touch-optimized controls
- Simplified chart toolbar

### Animation and Transitions

1. **Page Load**: Fade-in animation (0.5s)
2. **Filter Changes**: Smooth chart update (0.3s transition)
3. **Hover Effects**: Subtle elevation on cards
4. **Loading States**: Spinning indicator with primary color
5. **Data Updates**: Progressive rendering

### Accessibility Features

- **High Contrast**: All text meets WCAG AA standards
- **Focus Indicators**: Clear blue outlines on tab navigation
- **Screen Reader**: Proper ARIA labels on all controls
- **Keyboard Navigation**: Full functionality without mouse
- **Color Blind Safe**: Patterns in addition to colors

### Visual Hierarchy

1. **Primary Focus**: Main forecast chart
2. **Secondary**: Metric cards and current values
3. **Tertiary**: Sidebar controls and options
4. **Supporting**: Export buttons and metadata

### Empty States

When no data is available:
```
┌─────────────────────────────────────────┐
│                                         │
│         No forecast data available      │
│                                         │
│    Select parameters to view forecast   │
│                                         │
└─────────────────────────────────────────┘
```

### Loading States

```
┌─────────────────────────────────────────┐
│                                         │
│              ◐ Loading...               │
│                                         │
│      Fetching forecast data             │
│                                         │
└─────────────────────────────────────────┘
```

### Error States

```
┌─────────────────────────────────────────┐
│  ⚠️  Unable to load forecast            │
│                                         │
│  Please try again or contact support    │
│                                         │
│  [🔄 Retry]  [📧 Contact Support]      │
└─────────────────────────────────────────┘
```

## Approval Checklist

- [ ] Color scheme matches brand guidelines
- [ ] Typography is clear and readable
- [ ] Layout is intuitive and user-friendly
- [ ] Interactive elements are obvious
- [ ] Mobile design is acceptable
- [ ] Accessibility requirements are met
- [ ] Visual hierarchy guides user attention
- [ ] Overall design feels professional and modern

## Notes for Implementation

1. All measurements in rem units for scalability
2. CSS variables for easy theme changes
3. Component-based architecture for reusability
4. Performance optimized with lazy loading
5. Progressive enhancement approach