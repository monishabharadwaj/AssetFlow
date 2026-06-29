import { Tooltip } from "recharts";
import type { ComponentProps } from "react";

import { chartTooltipItemStyle, chartTooltipLabelStyle, chartTooltipStyle } from "@/lib/chart-theme";

type ChartTooltipProps = ComponentProps<typeof Tooltip>;

export function ChartTooltip(props: ChartTooltipProps) {
  return (
    <Tooltip
      contentStyle={chartTooltipStyle}
      labelStyle={chartTooltipLabelStyle}
      itemStyle={chartTooltipItemStyle}
      {...props}
    />
  );
}
