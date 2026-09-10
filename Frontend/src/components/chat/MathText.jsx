import { BlockMath, InlineMath } from "react-katex";
import "katex/dist/katex.min.css";

export function MathBlock({ value }) {
  if (!value) return null;
  return <BlockMath math={value} />;
}

export function MathInline({ value }) {
  if (!value) return null;
  return <InlineMath math={value} />;
}
