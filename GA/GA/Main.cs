using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GA
{
    class Main
    {
        // See https://aka.ms/new-console-template for more information
        static Random rand = new Random();
        public class Weight
        {
            public double[] val = new double[] { -80.0,10.0,20.0,- 16.0,- 06.0,- 0.0,3.0,- 12.0,2.0,3.0,5.6,3.2,- 2.9,3.3,1,2.9,1.0,1.8,0.3,1,- 0.6,0.1,- 2.5,5.5,1,2.1,4.0,1.3,- 2.5,1 };
            public void Print()
            {
                val.ToList().ForEach(x => Console.Write(Math.Round(x,1).ToString("0.0") + ","));
                Console.Write("\n");
            }
            public string ToText()
            {
                string res = "";
                val.ToList().ForEach(x => res+=Math.Round(x, 1).ToString("0.0") + ",");
                return res;
            }
            public void Mutate()
            {
                val = val.Select((s,i) => i<10?s + rand.Next() % 7 - 3:s+rand.NextDouble()-0.5).ToArray();
            }
        };
        public void Run()
        {
            var op = new Weight();
            StreamWriter wf = new StreamWriter("log3.txt");
            List<Weight> wlist = new();
            int size = 16;
            wlist.Add(new Weight());
            var path = @"C:\Users\Clover\Desktop\AI\Reversi\reversi.py";
            var eng = IronPython.Hosting.Python.CreateEngine();
            var scope = eng.CreateScope();
            eng.Execute(File.ReadAllText(path), scope);
            for(int i=0;i<size/2;i++)
                wlist.Add(new Weight());
            for (int i = size/2; i < size; i++)
                wlist.Add(RandWeight());
            for (int E = 0; E < 200; E++)
            {
                Console.WriteLine($"Epoch {E}");
                wf.WriteLine($"Epoch {E}");
                Dictionary<Weight, int> scores = new();
                wlist.ForEach(w => scores[w] = 0);
                for(int i=0;i<wlist.Count;i++)
                {
                    var w = wlist[i];
                    for (int j = 0; j < 2; j++)
                    {
                        var idx = rand.Next() % (wlist.Count);
                        var rivalW = wlist[idx];
                        var res= scope.GetVariable("play")(wlist[i].val, rivalW.val); 
                        scores[wlist[i]] += res;
                        scores[rivalW] -= res;
                        Console.WriteLine($"{i} vs {idx}-> {res}");
                    }
                }
                wlist = wlist.OrderBy(w => -scores[w]).ToList();
                Console.WriteLine("######");
                foreach (var w in wlist)
                {
                    wf.WriteLine("val "+w.ToText());
                    //w.Print();
                    int score = scope.GetVariable("play")(w.val, op.val);
                    wf.WriteLine("score "+score);
                    Console.WriteLine(score);
                }
                
                foreach (var w in wlist.Take(3))
                    w.Print();

                var newList = new List<Weight>();
                for (int i = 0; i < size / 2; i++)
                    for (int j = 0; j < 2; j++)
                        newList.Add(Cross(wlist[i], wlist[rand.Next() % (size / 2)]));
                wlist = newList;
                wlist.ForEach(x =>
                {
                    if (rand.Next() % 2 == 0)
                        x.Mutate();
                });
                wlist = wlist.Take(15).ToList();
                wlist.Add(RandWeight());
                if (wlist.Count != size)
                    throw new Exception("wrong size");
            }

            wf.Close();
        }

        Weight Cross(Weight a, Weight b)
        {
            Weight res = new();
            res.val = a.val.Select((item, i) => rand.NextDouble() > 0.5 ? a.val[i] : b.val[i]).ToArray();
            return res;
        }

        Weight RandWeight()
        {
            Weight res = new();
            for (int i = 0; i < 10; i++)
                res.val[i] = rand.Next() % 200 - 100;
            for (int i = 10; i < res.val.Length; i++)
                res.val[i] = rand.Next() % 20;
            return res;
        }

    }
}
