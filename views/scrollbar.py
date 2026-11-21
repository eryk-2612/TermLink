from .window import Window


def draw_vertical_scrollbar(
    parent_window,
    scrollbar_window,
    height,
    total,
    visible_count,
    scroll_offset,
    y,
    x,
    in_focus=True,
):
    """Draw the up/down indicators used by the scrollable views."""
    if not scrollbar_window:
        scrollbar_window = Window(height, 1, y, x, parent_window=parent_window)

    top_y = 1
    bottom_y = max(1, height - 2)
    can_scroll_up = scroll_offset > 0
    can_scroll_down = scroll_offset + visible_count < total
    show_indicators = total > visible_count and in_focus

    arrow_up = "▲" if can_scroll_up else "△"
    arrow_down = "▼" if can_scroll_down else "▽"
    if not show_indicators:
        arrow_up = arrow_down = " "

    if top_y == bottom_y:
        if can_scroll_up:
            scrollbar_window.write_simple(arrow_up, top_y, 0)
        elif can_scroll_down:
            scrollbar_window.write_simple(arrow_down, bottom_y, 0)
    else:
        scrollbar_window.write_simple(arrow_up, top_y, 0)
        scrollbar_window.write_simple(arrow_down, bottom_y, 0)

    return scrollbar_window
