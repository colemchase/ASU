import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

class VendingMachineTest
{
    @Test
    void vendingMachineCanBeConstructed()
    {
        assertNotNull(new VendingMachine());
    }

    @Test
    void candyWithExtraMoneyReturnsItemAndChange()
    {
        assertEquals(
                "Item dispensed and change of 10 returned",
                VendingMachine.dispenseItem(30, "candy")
        );
    }

    @Test
    void cokeWithExactMoneyReturnsItem()
    {
        assertEquals(
                "Item dispensed.",
                VendingMachine.dispenseItem(25, "coke")
        );
    }

    @Test
    void coffeeWithExactMoneyReturnsItem()
    {
        assertEquals(
                "Item dispensed.",
                VendingMachine.dispenseItem(45, "coffee")
        );
    }

    @Test
    void coffeeWithThirtyCentsReportsCandyOrCokeAlternative()
    {
        assertEquals(
                "Item not dispensed, missing 15 cents. Can purchase candy or coke.",
                VendingMachine.dispenseItem(30, "coffee")
        );
    }

    @Test
    void coffeeWithTwentyTwoCentsReportsCandyAlternative()
    {
        assertEquals(
                "Item not dispensed, missing 23 cents. Can purchase candy.",
                VendingMachine.dispenseItem(22, "coffee")
        );
    }

    @Test
    void coffeeWithTenCentsReportsNoAffordableItem()
    {
        assertEquals(
                "Item not dispensed, missing 35 cents. Cannot purchase item.",
                VendingMachine.dispenseItem(10, "coffee")
        );
    }
}
