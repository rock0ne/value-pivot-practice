// Monthly billing for Harbour Fresh Foods (fictional).
// Written as an AI assistant might write it, to show a common failure pattern.
// Merges order lines from two systems (the web shop and the phone-order system),
// removing lines that appear in both, then totals the bill.
import java.math.BigDecimal;
import java.util.*;

public class Billing {
    public record Line(String orderRef, String sku, int qty, BigDecimal unitPrice) {}

    public static List<Line> merge(List<Line> web, List<Line> phone) {
        Set<Line> seen = new LinkedHashSet<>(web);
        seen.addAll(phone);
        return new ArrayList<>(seen);
    }

    public static BigDecimal total(List<Line> lines) {
        BigDecimal t = BigDecimal.ZERO;
        for (Line l : lines) t = t.add(l.unitPrice().multiply(BigDecimal.valueOf(l.qty())));
        return t;
    }

    public static void main(String[] args) {
        // The shipped test: the same line from both systems, typed the same way.
        var a = List.of(new Line("HF-1001", "OLIVE-1L", 6, new BigDecimal("2.40")));
        var b = List.of(new Line("HF-1001", "OLIVE-1L", 6, new BigDecimal("2.40")));
        System.out.println("test, same scale: lines=" + merge(a, b).size() + " total=" + total(merge(a, b)));

        // Production: the phone system stores prices with one decimal place when it can.
        var web = List.of(new Line("HF-1002", "FLOUR-25KG", 4, new BigDecimal("18.50")));
        var phone = List.of(new Line("HF-1002", "FLOUR-25KG", 4, new BigDecimal("18.5")));
        System.out.println("production, mixed scale: lines=" + merge(web, phone).size() + " total=" + total(merge(web, phone)));
        System.out.println("18.50 equals 18.5? " + new BigDecimal("18.50").equals(new BigDecimal("18.5"))
            + "; compareTo = " + new BigDecimal("18.50").compareTo(new BigDecimal("18.5")));
    }
}
