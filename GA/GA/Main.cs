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
            public int[] val = new int[] { -100, 20, -20, -5, -1, -1,-1, 0, 2, 1, 0, 2, 1, 0, 2, 1, 5, 0, 0 };
            public void Print()
            {
                foreach(var x in val)
                {
                    Console.Write(x + " ");
                }
                Console.Write("\n");
            }
        };
        public class Cond
        {
            public int[] val = new int[] { 0,20,40,55};
        };
        public void Start()
        {
            Run().Wait();
        }
        public async Task Run()
        {
            Cond cond = new();
            List<Weight> wlist = new();
            int size = 8;
            wlist.Add(new Weight());
            for (int i = 1; i < size; i++)
                wlist.Add(RandWeight());
            var tasks = new List<Task<int>>();
            var rivalList = new List<int>();
            Dictionary<Weight, int> scores = new();
            foreach(var w in wlist)
            {
                scores[w] = 0;
                var rival = rand.Next() % (wlist.Count);
                rivalList.Add(rival);
                var rivalW = wlist[rival];
                tasks.Add(NewJob(w, cond, rivalW,cond));
            }
            for(int i=0;i<size;i++)
            {
                var res = await tasks[i];
                scores[wlist[i]] += res;
                scores[wlist[rivalList[i]]] -= res;
                Console.WriteLine($"Task {i} between {i} {rivalList[i]} finished with result {res}");
            }
            wlist.Sort((x,y) => scores[x]-scores[y]);
            foreach (var w in wlist) {
                w.Print();
             }
        }

        Weight Cross(Weight a, Weight b)
        {
            Weight res = new();
            res.val=a.val.Select((item, i) => rand.NextDouble() > 0.5 ? a.val[i] : b.val[i]).ToArray();
            return res;
        }

        Weight RandWeight()
        {
            Weight res = new();
            for(int i=0;i<7;i++)
                res.val[i] = rand.Next() % 100-50;
            for (int i = 7; i < res.val.Length; i++)
                res.val[i] = rand.Next() % 20;
            return res;
        }

        async Task<int> NewJob(Weight w0,Cond c0,Weight w1,Cond c1)
        {
            return await Task.Run(() =>
            {
                var path = @"C:\Users\Clover\Desktop\AI\Reversi\reversi.py";
                var eng = IronPython.Hosting.Python.CreateEngine();
                var scope = eng.CreateScope();
                eng.Execute(File.ReadAllText(path),scope);
                return scope.GetVariable("play")(w0.val,c0.val,w1.val,c1.val);
            });
        }


    }
}
