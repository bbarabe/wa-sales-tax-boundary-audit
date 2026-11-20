// Runs DOR's WaRateFileLookup 1.0.5 (unmodified library sources) against a list of test addresses.
// Input: tab-separated lines  id \t street \t city \t zip(5 or 9 with dash)
// Output: tab-separated result per line for both useShortcutEval=false and =true.
using System;
using System.IO;
using WaRateFiles;

class Driver
{
    static string Run(RateLookup lk, string street, string city, string zip)
    {
        AddressLine addr; Rate rate = null; LocationSource src;
        bool ok;
        try { ok = lk.FindRate(street, city, zip, out addr, ref rate, out src); }
        catch (Exception e) { return "EXCEPTION\t" + e.GetType().Name + ": " + e.Message + "\t\t\t"; }
        if (!ok || rate == null) return "NOTFOUND\t" + src + "\t\t\t";
        string row = addr == null ? "" :
            string.Format("{0}-{1} {2} {3}-{4:0000} code {5}", addr.HouseLow, addr.HouseHigh, addr.Street, addr.Zip5, addr.ZipPlus4, addr.LocationCode);
        return string.Format("{0}\t{1:0000}\t{2}\t{3}\t{4}", src, rate.LocationCodeInt, rate.LocationName, rate.TotalRate, row);
    }

    static int Main(string[] args)
    {
        string dir = args[0], tests = args[1];
        string a = Path.Combine(dir, "State_26Q4.txt"), r = Path.Combine(dir, "Rates_26Q4.csv"), z = Path.Combine(dir, "Zip4RatesQ42026-Short.txt");
        var full = new RateLookup(a, r, z, RateLookupEngine.STANDARDIZER, false);
        var shortcut = new RateLookup(a, r, z, RateLookupEngine.STANDARDIZER, true);
        Console.WriteLine("Period loaded: " + full.Period);
        foreach (var line in File.ReadAllLines(tests))
        {
            if (line.Trim().Length == 0 || line.StartsWith("#")) continue;
            var f = line.Split('\t');
            Console.WriteLine(f[0] + "\tFULL\t" + Run(full, f[1], f[2], f[3]));
            Console.WriteLine(f[0] + "\tSHORTCUT\t" + Run(shortcut, f[1], f[2], f[3]));
        }
        return 0;
    }
}
