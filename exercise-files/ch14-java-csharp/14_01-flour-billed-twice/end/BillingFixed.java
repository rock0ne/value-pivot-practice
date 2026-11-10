// The fix: normalise money to the currency's scale before it is ever compared,
// so that equal amounts are equal objects. setScale(2) throws if a price has
// more than two decimal places, which is what you want for pounds and pence.
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.*;

public class BillingFixed {
    public record Line(String orderRef, String sku, int qty, BigDecimal unitPrice) {
        public Line {
            unitPrice = unitPrice.setScale(2, RoundingMode.UNNECESSARY);
        }
    }

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
        var web = List.of(new Line("HF-1002", "FLOUR-25KG", 4, new BigDecimal("18.50")));
        var phone = List.of(new Line("HF-1002", "FLOUR-25KG", 4, new BigDecimal("18.5")));
        System.out.println("fixed, mixed scale: lines=" + merge(web, phone).size() + " total=" + total(merge(web, phone)));
        try {
            new Line("HF-1003", "SALT-1KG", 1, new BigDecimal("0.995"));
            System.out.println("three-decimal price accepted");
        } catch (ArithmeticException e) {
            System.out.println("three-decimal price refused");
        }
    }
}
