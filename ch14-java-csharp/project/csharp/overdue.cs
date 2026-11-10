// Overdue-invoice reminders for Harbour Fresh Foods (fictional).
// Written as an AI assistant might write it, to show a common failure pattern.
// Run with: dotnet run overdue.cs
using System;
using System.Collections.Generic;
using System.Linq;

var db = new FakeInvoiceDb(rows: 50_000);

IEnumerable<Invoice> overdue = db.ReadInvoices().Where(i => i.DueDate < new DateOnly(2026, 11, 1) && !i.Paid);

if (overdue.Any())
{
    Console.WriteLine($"overdue invoices: {overdue.Count()}");
    decimal owed = overdue.Sum(i => i.Amount);
    Console.WriteLine($"total owed: {owed:0.00}");
    int sent = 0;
    foreach (var inv in overdue) sent++;   // stands in for sending each reminder
    Console.WriteLine($"reminders queued: {sent}");
}
Console.WriteLine($"database reads: {db.Queries}, rows read: {db.RowsRead}");

public record Invoice(int Id, DateOnly DueDate, bool Paid, decimal Amount);

public class FakeInvoiceDb(int rows)
{
    public int Queries { get; private set; }
    public long RowsRead { get; private set; }

    // Stands in for a database query that streams every invoice row.
    public IEnumerable<Invoice> ReadInvoices()
    {
        Queries++;
        for (int i = 1; i <= rows; i++)
        {
            RowsRead++;
            yield return new Invoice(i, new DateOnly(2026, 1, 1).AddDays(i % 400), i % 7 != 0, 10m + i % 90);
        }
    }
}
